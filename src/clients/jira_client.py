import logging
from typing import List
from jira import JIRA
from src.models.schemas import JiraTicket, TicketStatus, BusinessInsight

logger = logging.getLogger(__name__)


class JiraClient:
    def __init__(self, jira_url: str, username: str, api_token: str, project_key: str):
        self.jira = JIRA(server=jira_url, basic_auth=(username, api_token))
        self.project_key = project_key
        
    def get_open_tickets(self, max_results: int = 10) -> List[JiraTicket]:
        """Fetch open tickets from JIRA that need data analysis."""
        jql_query = f'project = {self.project_key} AND labels = "data_analysis" AND status = "Open" ORDER BY created DESC'
        
        issues = self.jira.search_issues(jql_query, maxResults=max_results)
        tickets = []
        
        for issue in issues:
            ticket = JiraTicket(
                ticket_id=issue.key,
                summary=issue.fields.summary,
                description=issue.fields.description or "",
                status=TicketStatus.OPEN,
                assignee=issue.fields.assignee.displayName if issue.fields.assignee else None
            )
            tickets.append(ticket)
            
        return tickets
    
    def update_ticket_status(self, ticket_id: str, status: TicketStatus):
        """Update the status of a JIRA ticket."""
        issue = self.jira.issue(ticket_id)
        
        if status == TicketStatus.IN_PROGRESS:
            self.jira.transition_issue(issue, 'In Progress')
        elif status == TicketStatus.RESOLVED:
            self.jira.transition_issue(issue, 'Resolved')
        elif status == TicketStatus.CLOSED:
            self.jira.transition_issue(issue, 'Closed')
        
        logger.info(f"Updated ticket {ticket_id} status to {status.value}")
    
    def add_comment(self, ticket_id: str, comment: str):
        """Add a comment to a JIRA ticket."""
        issue = self.jira.issue(ticket_id)
        self.jira.add_comment(issue, comment)
        logger.info(f"Added comment to ticket {ticket_id}")
    
    def update_ticket_with_results(self, ticket_id: str, insight: BusinessInsight):
        """Update a JIRA ticket with analysis results."""
        issue = self.jira.issue(ticket_id)
        
        # Format the comment with insights
        comment = f"""
*Data Analysis Results*

*Summary:*
{insight.summary}

*Key Points:*
"""
        for point in insight.key_points:
            comment += f"- {point}\n"
            
        if insight.recommendations:
            comment += "\n*Recommendations:*\n"
            for rec in insight.recommendations:
                comment += f"- {rec}\n"
                
        # Add the comment to the ticket
        self.jira.add_comment(issue, comment)
        
        # Resolve the ticket
        self.update_ticket_status(ticket_id, TicketStatus.RESOLVED)
        
        logger.info(f"Updated ticket {ticket_id} with analysis results and resolved it")
