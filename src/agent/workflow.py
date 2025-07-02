import logging
from typing import Annotated, Literal
from langgraph.graph import StateGraph, END

from src.models.schemas import (
    JiraTicket, 
    SQLQuery, 
    ValidationResult, 
    QueryResult, 
    BusinessInsight,
    AgentState
)

logger = logging.getLogger(__name__)


def create_workflow(
    generate_sql_fn, 
    validate_sql_fn, 
    execute_query_fn, 
    validate_results_fn,
    generate_insights_fn,
    update_jira_fn,
    max_retries: int = 3
):
    """Create the agent workflow graph."""
    
    # Define state transitions
    def should_retry_query(state: AgentState) -> Literal["retry", "failed", "continue"]:
        """Check if we should retry generating SQL or move on."""
        if state.validation_result and state.validation_result.is_valid:
            return "continue"
        
        if state.retry_count < max_retries:
            return "retry"
        else:
            return "failed"
    
    def should_retry_execution(state: AgentState) -> Literal["retry", "failed", "continue"]:
        """Check if we should retry executing the query or move on."""
        if state.query_result:
            return "continue"
        
        if state.retry_count < max_retries:
            return "retry"
        else:
            return "failed"
    
    def process_results(state: AgentState) -> Literal["continue", "retry", "failed"]:
        """Check if results validation passed."""
        if state.validation_result and state.validation_result.is_valid:
            return "continue"
        
        if state.retry_count < max_retries:
            return "retry"
        else:
            return "failed"
    
    # Define the workflow nodes
    def extract_task(state: AgentState) -> AgentState:
        """Extract task from JIRA ticket."""
        logger.info(f"Extracting task from ticket {state.ticket.ticket_id}")
        task = state.ticket.description
        return AgentState(**{**state.model_dump(), "task_description": task})
    
    def generate_sql(state: AgentState) -> AgentState:
        """Generate SQL query from task description."""
        logger.info(f"Generating SQL for task: {state.task_description}")
        try:
            sql_query = generate_sql_fn(state.task_description)
            return AgentState(**{**state.model_dump(), "sql_query": sql_query, "error_message": None})
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return AgentState(**{**state.model_dump(), "error_message": str(e)})
    
    def validate_sql(state: AgentState) -> AgentState:
        """Validate the generated SQL query."""
        logger.info("Validating SQL query")
        if not state.sql_query:
            return AgentState(**{
                **state.model_dump(), 
                "validation_result": ValidationResult(is_valid=False, errors=["No SQL query to validate"])
            })
            
        validation_result = validate_sql_fn(state.sql_query, state.task_description)
        return AgentState(**{**state.model_dump(), "validation_result": validation_result})
    
    def execute_query(state: AgentState) -> AgentState:
        """Execute the validated SQL query."""
        logger.info("Executing SQL query")
        try:
            query_result = execute_query_fn(state.sql_query.query)
            return AgentState(**{**state.model_dump(), "query_result": query_result, "error_message": None})
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return AgentState(**{**state.model_dump(), "error_message": str(e)})
    
    def validate_results(state: AgentState) -> AgentState:
        """Validate the query results."""
        logger.info("Validating query results")
        if not state.query_result:
            return AgentState(**{
                **state.model_dump(), 
                "validation_result": ValidationResult(is_valid=False, errors=["No query results to validate"])
            })
            
        validation_result = validate_results_fn(state.query_result, state.task_description)
        return AgentState(**{**state.model_dump(), "validation_result": validation_result})
    
    def generate_insights(state: AgentState) -> AgentState:
        """Generate business insights from query results."""
        logger.info("Generating business insights")
        if not state.query_result:
            return AgentState(**{
                **state.model_dump(), 
                "business_insight": BusinessInsight(
                    summary="Unable to generate insights - no query results available.", 
                    key_points=["Query execution failed."]
                )
            })
            
        insights = generate_insights_fn(state.task_description, state.query_result)
        return AgentState(**{**state.model_dump(), "business_insight": insights})
    
    def update_jira_ticket(state: AgentState) -> AgentState:
        """Update JIRA ticket with insights."""
        logger.info(f"Updating JIRA ticket {state.ticket.ticket_id}")
        if state.business_insight:
            update_jira_fn(state.ticket.ticket_id, state.business_insight)
        else:
            # Handle failure case
            error_insight = BusinessInsight(
                summary="Task processing failed",
                key_points=[state.error_message or "Unknown error occurred"]
            )
            update_jira_fn(state.ticket.ticket_id, error_insight, failed=True)
            
        return state
    
    def increment_retry(state: AgentState) -> AgentState:
        """Increment the retry counter."""
        logger.info(f"Incrementing retry counter from {state.retry_count} to {state.retry_count + 1}")
        return AgentState(**{**state.model_dump(), "retry_count": state.retry_count + 1})
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_task", extract_task)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("execute_query", execute_query)
    workflow.add_node("validate_results", validate_results)
    workflow.add_node("generate_insights", generate_insights)
    workflow.add_node("update_jira", update_jira_ticket)
    workflow.add_node("increment_retry", increment_retry)
    
    # Add edges
    workflow.add_edge("extract_task", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")
    
    # SQL validation branching
    workflow.add_conditional_edges(
        "validate_sql",
        should_retry_query,
        {
            "continue": "execute_query",
            "retry": "increment_retry",
            "failed": "update_jira"
        }
    )
    
    workflow.add_edge("increment_retry", "generate_sql")
    
    # Query execution branching
    workflow.add_conditional_edges(
        "execute_query",
        should_retry_execution,
        {
            "continue": "validate_results",
            "retry": "increment_retry",
            "failed": "update_jira"
        }
    )
    
    # Results validation branching
    workflow.add_conditional_edges(
        "validate_results",
        process_results,
        {
            "continue": "generate_insights",
            "retry": "increment_retry",
            "failed": "update_jira"
        }
    )
    
    workflow.add_edge("generate_insights", "update_jira")
    workflow.add_edge("update_jira", END)
    
    # Set the entry point
    workflow.set_entry_point("extract_task")
    
    return workflow.compile()
