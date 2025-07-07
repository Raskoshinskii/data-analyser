import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv

from src.clients.jira_client import JiraClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# load environment variables
load_dotenv()

# JIRA connection parameters
JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL")
JIRA_USER_EMAIL = os.environ.get("JIRA_USER_EMAIL")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY")
ISSUE_KEY = 'all'

if None in (JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY):
    logger.error(f"Configure Jira Environment Variables in .env file!")
    sys.exit(1)


def delete_jira_tickets():
    """Delete all JIRA tickets for the specified project."""
    logger.info("Connecting to JIRA...")
    try:
        jira = JiraClient(
            base_url=JIRA_BASE_URL, email=JIRA_USER_EMAIL, api_token=JIRA_API_TOKEN
        )
        logger.info("Connected to JIRA successfully")
    except Exception as e:
        logger.error(f"Failed to connect to JIRA: {e}")
        sys.exit(1)

    try:
        jira.delete_issues(project_key=JIRA_PROJECT_KEY, issue_key=ISSUE_KEY)
        logger.info(f"All issues in project {JIRA_PROJECT_KEY} deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete issues: {e}")

if __name__ == "__main__":
    delete_jira_tickets()