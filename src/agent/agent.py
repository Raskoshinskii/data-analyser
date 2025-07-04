import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

from src.agent.workflow import create_workflow
from src.clients.jira_client import JiraClient
from src.models.schemas import AgentState, JiraTicket
from src.tools.insight_tool import InsightTool
from src.tools.sql_tool import SQLTool
from src.tools.validator_tool import ValidatorTool

load_dotenv()

logger = logging.getLogger(__name__)


class DataAnalysisAgent:
    def __init__(self, agent_config: str, db_client: Any, max_retries: int = 3):
        self.config = self._load_yaml_config(agent_config)
        self.max_retries = max_retries

        # initialize clients
        self.db_client = db_client
        self.db_schema = self.db_client.get_database_schema()
        self.jira_client = JiraClient(
            base_url=os.environ.get("JIRA_BASE_URL"),
            email=os.environ.get("JIRA_USER_EMAIL"),
            api_token=os.environ.get("JIRA_API_TOKEN"),
        )

        # initialize LLM
        self.llm = ChatOpenAI(
            model=self.config["agent"]["llm"]["model_name"],
            temperature=self.config["agent"]["llm"]["temperature"],
            max_tokens=self.config["agent"]["llm"]["max_tokens"],
        )

        # initialize tools
        self.sql_generation_tool = SQLTool(llm=self.llm, db_schema=self.db_schema)
        self.sql_validation_tool = ValidatorTool(
            llm=self.llm, schema_dict=self.db_schema
        )
        self.sql_insight_tool = InsightTool(llm=self.llm)

        # langgraph workflow
        self.workflow = self._create_agent_workflow()

    def _load_yaml_config(self, path: str | Path) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(path, "r") as file:
            return yaml.safe_load(file)

    def _create_agent_workflow(self) -> StateGraph:
        return create_workflow(agent=self, max_retries=self.max_retries)

    def process_ticket(self, ticket: JiraTicket) -> None:
        """Process a single JIRA ticket."""
        logger.info(f"Processing ticket {ticket.ticket_id}")

        # define initial agent state
        initial_state = AgentState(ticket=ticket)

        # execute the workflow
        final_state = self.workflow.invoke(initial_state)
        final_state = AgentState.model_validate(
            final_state
        )  # convert back to Pydantic model (AgentState)

        if final_state.business_insight:
            logger.info(f"Successfully processed ticket {ticket.ticket_id}")
        else:
            logger.error(f"Failed to process ticket {ticket.ticket_id}")


# drop later
# def create_jira_ticket(self, summary, description, issue_type='Task', **kwargs):
#     """Create a JIRA ticket."""
#     return self.jira_client.create_issue(
#         project_key=self.project_key,
#         summary=summary,
#         description=description,
#         issue_type=issue_type,
#         component='Analysis',  # Use appropriate component name based on your Jira setup
#         additional_fields=kwargs.get('additional_fields', {})
#     )

# def _create_agent_workflow(self) -> StateGraph:
#     """Create the agent workflow."""
#     return create_workflow(
#         generate_sql_fn=lambda task: self.sql_tool.generate_query(task, self.schema),
#         validate_sql_fn=lambda query, task: self.validator_tool.validate_sql(query, task),
#         execute_query_fn=lambda query: self.db_client.execute_query(query),
#         validate_results_fn=lambda results, task: self.validator_tool.validate_query_results(results, task),
#         generate_insights_fn=lambda task, results: self.insight_tool.generate_insights(task, results),
#         update_jira_fn=lambda ticket_id, insights, failed=False: self.jira_client.update_ticket_with_results(ticket_id, insights),
#         max_retries=self.config["agent"]["max_retries"]
#     )


# def process_open_tickets(self, max_tickets: int = 5) -> List[BusinessInsight]:
#     """Process all open data analysis tickets."""
#     open_tickets = self.jira_client.get_open_tickets(max_results=max_tickets)

#     logger.info(f"Found {len(open_tickets)} open data analysis tickets")

#     results = []
#     for ticket in open_tickets:
#         insight = self.process_ticket(ticket)
#         results.append(insight)

#     return results

# def create_jira_ticket(self, summary, description, issue_type='Task', **kwargs):
#     """Create a JIRA ticket."""
#     return self.jira_client.create_issue(
#         project_key=self.project_key,
#         summary=summary,
#         description=description,
#         issue_type=issue_type,
#         component='Analysis',  # Use appropriate component name based on your Jira setup
#         additional_fields=kwargs.get('additional_fields', {})
#     )
