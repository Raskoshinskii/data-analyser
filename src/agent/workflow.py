import logging
from typing import Any, Literal

from langgraph.graph import END, StateGraph

from src.models.schemas import AgentState, BusinessInsight, ValidationResult

logger = logging.getLogger(__name__)


def create_workflow(agent: Any, max_retries: int = 3):
    from src.agent.agent import DataAnalysisAgent

    """Create the agent workflow graph."""

    def check_validation_results(
        state: AgentState,
    ) -> Literal["continue", "retry", "failed"]:
        """Check validation results of agent state."""
        if state.validation_result and state.validation_result.is_valid:
            return "continue"

        if state.retry_count < max_retries:
            return "retry"
        else:
            return "failed"

    def check_sql_execution(
        state: AgentState,
    ) -> Literal["retry", "failed", "continue"]:
        """Check if we should retry executing the query or move on."""
        if state.query_result:
            return "continue"

        if state.retry_count < max_retries:
            return "retry"
        else:
            return "failed"

    def increment_retry(state: AgentState) -> AgentState:
        """Increment the retry counter."""
        logger.info(
            f"Incrementing retry counter from {state.retry_count} to {state.retry_count + 1}"
        )
        return state.model_copy(update={"retry_count": state.retry_count + 1})

    def set_agent_task_from_ticket(state: AgentState) -> AgentState:
        """Extract task from JIRA ticket."""
        logger.info(f"Extracting task from ticket {state.ticket.ticket_id}")
        task = state.ticket.description
        return state.model_copy(update={"current_task": task})

    def generate_sql(
        state: AgentState,
    ) -> AgentState:
        """Generate SQL query from task description."""
        logger.info(f"Generating SQL for the current task")
        try:
            sql_query = agent.sql_generation_tool.generate_query(
                task_description=state.current_task
            )
            return state.model_copy(
                update={"sql_query": sql_query, "error_message": None}
            )
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return state.model_copy(update={"error_message": str(e)})

    def validate_sql(state: AgentState) -> AgentState:
        """Validate the generated SQL query."""
        logger.info("Validating SQL query")
        if not state.sql_query:
            return state.model_copy(
                update={
                    "validation_result": ValidationResult(
                        is_valid=False, errors=["No SQL query to validate"]
                    )
                }
            )

        validation_result = agent.sql_validation_tool.validate_sql(
            sql_query=state.sql_query
        )
        return state.model_copy(update={"validation_result": validation_result})

    def execute_sql(state: AgentState) -> AgentState:
        """Execute the validated SQL query."""
        logger.info("Executing SQL query")
        try:
            query_result = agent.db_client.execute_query(state.sql_query)
            return state.model_copy(
                update={"query_result": query_result, "error_message": None}
            )
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return state.model_copy(update={"error_message": str(e)})

    def generate_insights(state: AgentState) -> AgentState:
        """Generate business insights from query results."""
        logger.info("Generating business insights")
        if not state.query_result:
            return state.model_copy(
                update={
                    "business_insight": BusinessInsight(
                        summary="Unable to generate insights - no query results available.",
                        key_points=["Query execution failed."],
                    )
                }
            )

        insights = agent.sql_insight_tool.generate_insights(
            task_description=state.current_task, query_result=state.query_result
        )
        return state.model_copy(update={"business_insight": insights})

    def update_jira_ticket(
        state: AgentState, ticket_status: str = "In Progress"
    ) -> AgentState:
        """Update JIRA ticket with insights."""
        logger.info(f"Updating JIRA ticket {state.ticket.ticket_id}")

        # ticket status update
        agent.jira_client.transition_issue(
            issue_key=state.ticket.ticket_id, status_name="В работе"
        )

        # add comment with business insights
        if not state.business_insight:
            error_comment = "Sorry, I cannot generate insights for this task."
            agent.jira_client.add_comment(
                issue=state.ticket.ticket_id, comment=error_comment
            )
            return state

        agent.jira_client.add_comment(
            issue=state.ticket.ticket_id, comment=state.business_insight
        )
        return state

    # build graph (langgraph)
    workflow = StateGraph(AgentState)

    # define nodes
    workflow.add_node("extract_task", set_agent_task_from_ticket)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("execute_sql", execute_sql)
    # TODO: align later on if we need query results validation!
    # workflow.add_node("validate_results", validate_results)
    workflow.add_node("generate_insights", generate_insights)
    workflow.add_node("update_jira_ticket", update_jira_ticket)
    workflow.add_node("increment_retry", increment_retry)

    # define edges between nodes
    workflow.add_edge("extract_task", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")

    # SQL syntax validation logic (coditional edge)
    workflow.add_conditional_edges(
        "validate_sql",
        check_validation_results,
        {
            "continue": "execute_sql",
            "retry": "increment_retry",
            "failed": "update_jira_ticket",
        },
    )
    # if validation fails -> increment retry and run "generate_sql" function again
    workflow.add_edge("increment_retry", "generate_sql")

    # SQL execution validation logic
    workflow.add_conditional_edges(
        "execute_sql",
        check_sql_execution,
        {
            "continue": "generate_insights",
            "retry": "increment_retry",  # if validation fails -> increment retry and run "generate_sql" function again
            "failed": "update_jira_ticket",
        },
    )

    # final edges
    workflow.add_edge("generate_insights", "update_jira_ticket")
    workflow.add_edge("update_jira_ticket", END)

    # set the entry point of the workflow and build the workflow
    workflow.set_entry_point("extract_task")
    return workflow.compile()


# delete later
# # Results validation branching
# workflow.add_conditional_edges(
#     "validate_results",
#     process_results,
#     {
#         "continue": "generate_insights",
#         "retry": "increment_retry",
#         "failed": "update_jira"
#     }
# )


# def validate_results(state: AgentState) -> AgentState:
#     """Validate the query results."""
#     logger.info("Validating query results")
#     if not state.query_result:
#         return AgentState(**{
#             **state.model_dump(),
#             "validation_result": ValidationResult(is_valid=False, errors=["No query results to validate"])
#         })

#     validation_result = validate_results_fn(state.query_result, state.task_description)
#     return AgentState(**{**state.model_dump(), "validation_result": validation_result})
