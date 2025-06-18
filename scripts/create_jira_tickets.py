import logging
import time
import os
from jira import JIRA
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# JIRA connection parameters
JIRA_URL = os.environ.get('JIRA_URL', 'http://localhost:8080')
JIRA_USER = os.environ.get('JIRA_USER', 'admin')
JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD', 'admin')  # This should be changed after first login
PROJECT_KEY = os.environ.get('JIRA_PROJECT_KEY', 'DATA')

# Sample data analysis tickets
sample_tickets = [
    {
        'summary': 'Car Models Analysis',
        'description': 'How many unqiue car models we have per car category? Sort the results in descending order!',
        'labels': ['data_analysis', 'sales', 'quarterly']
    },
    {
        'summary': 'Dealership Performance by Region Analysis',
        'description': 'Analyze the average dealership rating and sales capacity by region. Which regions have the highest performing dealerships? Sort the results by average rating in descending order.',
        'labels': ['data_analysis', 'dealerships', 'regional']
    }
    {
        'summary': 'Service Cost Analysis by Model and Service Type',
        'description': 'Analyze the average service costs by model and service type. Identify which models have higher maintenance costs and which service types contribute most to overall service revenue.',
        'labels': ['data_analysis', 'service', 'costs']
    },
]

def setup_jira_project():
    """Set up JIRA project and create sample tickets"""
    logger.info("Connecting to JIRA...")
    
    # Wait for JIRA to be ready
    retries = 0
    while retries < 30:
        try:
            jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_USER, JIRA_PASSWORD))
            # Test connection by getting server info
            jira.server_info()
            logger.info("Connected to JIRA successfully")
            break
        except Exception as e:
            logger.warning(f"JIRA not ready yet: {str(e)}")
            retries += 1
            time.sleep(10)
    
    if retries == 30:
        logger.error("Could not connect to JIRA after multiple attempts")
        return

    try:
        # Check if project already exists
        try:
            project = jira.project(PROJECT_KEY)
            logger.info(f"Project {PROJECT_KEY} already exists")
        except Exception:
            # Create project if it doesn't exist
            logger.info(f"Creating project {PROJECT_KEY}...")
            project_dict = {
                'key': PROJECT_KEY,
                'name': 'Data Analysis',
                'projectTypeKey': 'business',
                'projectTemplateKey': 'com.atlassian.jira-core-project-templates:jira-core-project-management',
                'leadAccountId': jira.myself()['accountId'],
            }
            project = jira.create_project(
                key=PROJECT_KEY,
                name='Data Analysis',
                projectTypeKey='business'
            )
            logger.info(f"Project {PROJECT_KEY} created successfully")

        # Create tickets
        logger.info("Creating sample tickets...")
        for ticket in sample_tickets:
            issue_dict = {
                'project': {'key': PROJECT_KEY},
                'summary': ticket['summary'],
                'description': ticket['description'],
                'issuetype': {'name': 'Task'},
                'labels': ticket['labels']
            }
            
            # Old code using deprecated syntax
            # issue = jira.create_issue(fields=issue_dict)
            
            # New code with component parameter
            issue = jira.create_issue(
                project_key=PROJECT_KEY,
                summary=ticket['summary'],
                description=ticket['description'],
                issue_type='Task',
                component='General',  # Add appropriate component name
                additional_fields={'labels': ticket['labels']}
            )
            
            logger.info(f"Created ticket {issue.key}: {ticket['summary']}")
        
        logger.info("JIRA setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up JIRA: {str(e)}")

if __name__ == "__main__":
    setup_jira_project()
