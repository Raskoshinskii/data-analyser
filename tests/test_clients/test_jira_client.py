import pytest
from unittest.mock import patch, MagicMock

from src.clients.jira_client import JiraClient


@patch('src.clients.jira_client.JIRA')
def test_jira_client_initialization(mock_jira):
    """Test the initialization of the JiraClient."""
    # Setup
    mock_jira_instance = MagicMock()
    mock_jira.return_value = mock_jira_instance
    mock_jira_instance.myself.return_value = {"accountId": "test-account-id"}
    
    # Create the client
    client = JiraClient(base_url="https://example.atlassian.net", 
                        email="test@example.com", 
                        api_token="test-token")
    
    # Assertions
    mock_jira.assert_called_once_with(
        server="https://example.atlassian.net",
        basic_auth=("test@example.com", "test-token")
    )
    assert client.jira == mock_jira_instance
    assert client.account_id == "test-account-id"


@patch('src.clients.jira_client.JIRA')
def test_get_active_issues(mock_jira):
    """Test getting active issues."""
    # Setup
    mock_jira_instance = MagicMock()
    mock_jira.return_value = mock_jira_instance
    mock_jira_instance.myself.return_value = {"accountId": "test-account-id"}
    
    mock_issues = [MagicMock(), MagicMock()]
    mock_jira_instance.search_issues.return_value = mock_issues
    
    # Create the client
    client = JiraClient(base_url="https://example.atlassian.net", 
                        email="test@example.com", 
                        api_token="test-token")
    
    # Get active issues
    issues = client.get_active_issues()
    
    # Assertions
    assert issues == mock_issues
    mock_jira_instance.search_issues.assert_called_once()


@patch('src.clients.jira_client.JIRA')
def test_get_issue(mock_jira):
    """Test getting a specific issue."""
    # Setup
    mock_jira_instance = MagicMock()
    mock_jira.return_value = mock_jira_instance
    mock_jira_instance.myself.return_value = {"accountId": "test-account-id"}
    
    mock_issue = MagicMock()
    mock_jira_instance.issue.return_value = mock_issue
    
    # Create the client
    client = JiraClient(base_url="https://example.atlassian.net", 
                        email="test@example.com", 
                        api_token="test-token")
    
    # Get issue
    issue = client.get_issue(issue="DATA-1")
    
    # Assertions
    assert issue == mock_issue
    mock_jira_instance.issue.assert_called_once_with("DATA-1")


@patch('src.clients.jira_client.JIRA')
def test_get_comments(mock_jira):
    """Test getting comments for an issue."""
    # Setup
    mock_jira_instance = MagicMock()
    mock_jira.return_value = mock_jira_instance
    mock_jira_instance.myself.return_value = {"accountId": "test-account-id"}
    
    mock_comments = {"comments": [{"body": "Test comment"}]}
    mock_jira_instance.comments.return_value = mock_comments
    
    # Create the client
    client = JiraClient(base_url="https://example.atlassian.net", 
                        email="test@example.com", 
                        api_token="test-token")
    
    # Get comments
    comments = client.get_comments(issue_key="DATA-1")
    
    # Assertions
    assert comments == mock_comments
    mock_jira_instance.comments.assert_called_once_with("DATA-1")


@patch('src.clients.jira_client.JIRA')
def test_add_comment(mock_jira):
    """Test adding a comment to an issue."""
    # Setup
    mock_jira_instance = MagicMock()
    mock_jira.return_value = mock_jira_instance
    mock_jira_instance.myself.return_value = {"accountId": "test-account-id"}
    
    # Create the client
    client = JiraClient(base_url="https://example.atlassian.net", 
                        email="test@example.com", 
                        api_token="test-token")
    
    # Add comment
    client.add_comment(issue="DATA-1", comment="Test comment")
    
    # Assertions
    mock_jira_instance.add_comment.assert_called_once_with("DATA-1", "Test comment")


@patch('src.clients.jira_client.JIRA')
def test_extract_issue_details(mock_jira):
    """Test extracting issue details."""
    # Setup
    mock_jira_instance = MagicMock()
    mock_jira.return_value = mock_jira_instance
    mock_jira_instance.myself.return_value = {"accountId": "test-account-id"}
    
    mock_issue = MagicMock()
    mock_issue.key = "DATA-1"
    mock_issue.fields.summary = "Test Summary"
    mock_issue.fields.description = "Test Description"
    mock_issue.fields.status.name = "Open"
    
    # Create the client
    client = JiraClient(base_url="https://example.atlassian.net", 
                        email="test@example.com", 
                        api_token="test-token")
    
    # Extract issue details
    details = client.extract_issue_details(mock_issue)
    
    # Assertions
    assert details["ticket_id"] == "DATA-1"
    assert details["summary"] == "Test Summary"
    assert details["description"] == "Test Description"
    assert details["status"] == "Open"