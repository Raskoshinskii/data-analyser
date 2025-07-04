import logging
import os
from typing import Any, List

from dotenv import load_dotenv

from src.agent.agent import DataAnalysisAgent
from src.clients.db_client import DatabaseClient
from src.clients.jira_client import JiraClient
from src.models.schemas import JiraTicket

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("data_analyzer.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)
load_dotenv()

# JIRA parameters
JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL")
JIRA_USER_EMAIL = os.environ.get("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY")

# Database parameters
DB_PATH = "./data/porsche_analytics.db"
SQLITE_CONNECTION_STRING = f"sqlite:///{DB_PATH}"


def get_active_issue_ids_from_jira(jira_clinet: Any):
    """Get active tickets from JIRA."""
    # get issues ids assigned to the bot
    active_issues = jira_clinet.get_active_issues()
    issue_keys = [issue["key"] for issue in active_issues]

    # rule: if the last comment from bot -> no need to process the ticket
    issue_ids = []
    for issue in issue_keys:
        # TODO: improve in the future (API call in a loop -> slow)
        response = jira_clinet.get_comments(issue_key=issue)

        # if empty comments -> process
        if not response["comments"]:
            issue_ids.append(issue)
        else:
            last_comment = response["comments"][-1]
            if last_comment["author"]["accountId"] != jira_clinet.account_id:
                issue_ids.append(issue)
    return issue_ids


def get_jira_tickets(jira_clinet: Any, issue_ids: List[str]):
    tickets = []
    active_issue_ids = get_active_issue_ids_from_jira(jira_clinet=jira_clinet)
    for issue_id in active_issue_ids:
        issue = jira_clinet.get_issue(issue=issue_id)
        tickets.append(jira_clinet.extract_issue_details(issue))
    return tickets


def main(agen_config: str) -> None:
    # load environment variables
    load_dotenv()

    # define clients
    jira = JiraClient(
        base_url=JIRA_BASE_URL, email=JIRA_USER_EMAIL, api_token=JIRA_API_TOKEN
    )
    sqlite_client = DatabaseClient(SQLITE_CONNECTION_STRING)
    agent = DataAnalysisAgent(
        agent_config=agen_config, db_client=sqlite_client, max_retries=3
    )

    try:
        # get active issues from JIRA (assigned to the bot)
        issue_ids = get_active_issue_ids_from_jira(jira_clinet=jira)
        jira_tickets = get_jira_tickets(jira_clinet=jira, issue_ids=issue_ids)

        # process each ticket
        logger.info(f"Found {len(jira_tickets)} issues to process")
        for jira_ticket in jira_tickets:
            # transfrom raw dict into JiraTicket (pydantic model)
            jira_ticket = JiraTicket(
                ticket_id=jira_ticket["ticket_id"],
                summary=jira_ticket["summary"],
                description=jira_ticket["description"],
                status=jira_ticket["status"],
            )

            agent.process_ticket(ticket=jira_ticket)

    except Exception as e:
        logger.error(f"Error in main function call: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main(agen_config="./config/config.yaml")
