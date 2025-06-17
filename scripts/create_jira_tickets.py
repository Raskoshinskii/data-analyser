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
        'summary': 'Sales trend analysis by model for Q1 2023',
        'description': 'Please analyze the sales performance of different Porsche models during Q1 2023. Compare with previous quarters and identify top-performing models and any emerging trends.',
        'labels': ['data_analysis', 'sales', 'quarterly']
    },
    {
        'summary': 'Customer demographics by model preference',
        'description': 'Analyze the relationship between customer demographics (age, location) and their preferred Porsche models. Which models are most popular in different regions and age groups?',
        'labels': ['data_analysis', 'customers', 'demographics']
    },
    {
        'summary': 'Service frequency analysis by vehicle age',
        'description': 'Investigate how the frequency of service visits correlates with vehicle age and model. Do certain models require more maintenance as they age? Are there any common issues emerging at specific mileage points?',
        'labels': ['data_analysis', 'service', 'maintenance']
    },
    {
        'summary': 'Dealership performance comparison',
        'description': 'Compare the performance of our dealerships across different regions. Analysis should include sales volume, service revenue, and customer satisfaction metrics. Identify top performers and potential areas for improvement.',
        'labels': ['data_analysis', 'dealership', 'performance']
    },
    {
        'summary': 'Color popularity analysis by model and region',
        'description': 'Analyze which colors are most popular for different Porsche models. Include regional preferences in your analysis. Are there any interesting patterns or shifts in color preferences over time?',
        'labels': ['data_analysis', 'sales', 'preferences']
    },
    {
        'summary': 'Customer retention rate analysis',
        'description': 'Calculate and analyze customer retention rates. What percentage of customers purchase another Porsche? Is there any correlation between service satisfaction and repeat purchases? How long is the typical upgrade cycle?',
        'labels': ['data_analysis', 'customers', 'retention']
    },
    {
        'summary': 'Electric vs. conventional model adoption trends',
        'description': 'Compare the sales growth and customer demographics between our electric models (Taycan) and conventional models. What trends can we identify in the electric vehicle adoption? Which regions show the highest EV uptake?',
        'labels': ['data_analysis', 'sales', 'electric_vehicles']
    },
    {
        'summary': 'Service cost analysis by model and service type',
        'description': 'Analyze the average service costs by model and service type. Identify which models have higher maintenance costs and which service types contribute most to overall service revenue.',
        'labels': ['data_analysis', 'service', 'costs']
    }
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
            
            issue = jira.create_issue(fields=issue_dict)
            logger.info(f"Created ticket {issue.key}: {ticket['summary']}")
        
        logger.info("JIRA setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up JIRA: {str(e)}")

if __name__ == "__main__":
    setup_jira_project()
