import os
import sys
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.clients.jira_client import JiraClient
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# load environment variables
load_dotenv()

# JIRA connection parameters
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL')
JIRA_USER_EMAIL = os.environ.get('JIRA_USER_EMAIL')
JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN') 
JIRA_PROJECT_KEY = os.environ.get('JIRA_PROJECT_KEY')

if None in (JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY):
    logger.error(f"Configure Jira Environment Variables in .env file!")
    sys.exit(1)

# sample data analysis tickets
tickets = [
    {
        'project': JIRA_PROJECT_KEY,
        'summary': 'Car Models Analysis',
        'description': 'How many unqiue car models we have per car category? Sort the results in descending order!',
        'issuetype': 'Task',
    },
    {
        'project': JIRA_PROJECT_KEY,
        'summary': 'Dealership Performance by Region Analysis',
        'description': 'Analyze the average dealership rating and sales capacity by region. Which regions have the highest performing dealerships? Sort the results by average rating in descending order.',
        'issuetype': 'Task',
    },
    {
        'project': JIRA_PROJECT_KEY,
        'summary': 'Service Cost Analysis by Model and Service Type',
        'description': 'Analyze the average service costs by model and service type. Identify which models have higher maintenance costs and which service types contribute most to overall service revenue.',
        'issuetype': 'Task',
    },
]


def create_jira_tickets():
    """Set up JIRA project and create sample tickets"""
    logger.info("Connecting to JIRA...")
    try:
        jira = JiraClient(
            base_url=JIRA_BASE_URL,
            email=JIRA_USER_EMAIL,
            api_token=JIRA_API_TOKEN
        )
        logger.info("Connected to JIRA successfully")
    except Exception as e:
        logger.error(f"Failed to connect to JIRA: {str(e)}")

    logger.info("Project Setup in progress...")
    # TODO: Implement project setup logic (my Jira account cannot create projects | Vlad)

    # issues creation
    logger.info("Creating Tickets...")

    try:
        for ticket_info in tickets:
            resposne = jira.create_issue(ticket_info)
            resposne = logger.info(f"Created Ticket -> {resposne['key']}")
        logger.info("Tickets Created Successfully!")
    except Exception as e:
        logger.error(f"Failed to Create Tickets: {str(e)}")


if __name__ == "__main__":
    create_jira_tickets()
