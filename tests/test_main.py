import pytest
from unittest.mock import patch, MagicMock

from main import get_active_issue_ids_from_jira, get_jira_tickets, main


def test_get_active_issue_ids_from_jira_empty_comments(mock_jira_client, sample_issue_comments_empty):
    """Test getting active issue IDs with empty comments."""
    # Override the get_comments return value for this test
    mock_jira_client.get_comments.return_value = sample_issue_comments_empty
    
    result = get_active_issue_ids_from_jira(mock_jira_client)
    
    assert isinstance(result, list)
    assert len(result) == 2  # Based on our mock that returns 2 issues
    assert "DATA-1" in result
    assert "DATA-2" in result


def test_get_active_issue_ids_from_jira_with_bot_last(mock_jira_client, sample_issue_comments_with_bot_last):
    """Test getting active issue IDs with bot as last commenter."""
    # Override the get_comments return value for this test
    mock_jira_client.get_comments.return_value = sample_issue_comments_with_bot_last
    
    result = get_active_issue_ids_from_jira(mock_jira_client)
    
    assert isinstance(result, list)
    assert len(result) == 0  # Should be empty since bot was last commenter


def test_get_active_issue_ids_from_jira_with_user_last(mock_jira_client, sample_issue_comments_with_user_last):
    """Test getting active issue IDs with user as last commenter."""
    # Override the get_comments return value for this test
    mock_jira_client.get_comments.return_value = sample_issue_comments_with_user_last
    
    result = get_active_issue_ids_from_jira(mock_jira_client)
    
    assert isinstance(result, list)
    assert len(result) == 2  # Should include both issues since user was last commenter


def test_get_jira_tickets(mock_jira_client):
    """Test getting JIRA tickets."""
    # Patch the get_active_issue_ids_from_jira function to return a fixed list
    with patch('main.get_active_issue_ids_from_jira', return_value=["DATA-1", "DATA-2"]):
        result = get_jira_tickets(mock_jira_client, ["DATA-1", "DATA-2"])
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["ticket_id"] == "DATA-1"
        assert result[0]["summary"] == "Test Ticket"


@patch('main.JiraClient')
@patch('main.DatabaseClient')
@patch('main.DataAnalysisAgent')
@patch('main.get_active_issue_ids_from_jira')
@patch('main.get_jira_tickets')
def test_main_function(mock_get_jira_tickets, mock_get_active_ids, 
                     mock_agent_class, mock_db_client_class, mock_jira_client_class):
    """Test the main function."""
    # Setup the mocks
    mock_jira_client = MagicMock()
    mock_jira_client_class.return_value = mock_jira_client
    
    mock_db_client = MagicMock()
    mock_db_client_class.return_value = mock_db_client
    
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent
    
    mock_get_active_ids.return_value = ["DATA-1", "DATA-2"]
    
    mock_get_jira_tickets.return_value = [
        {
            "ticket_id": "DATA-1",
            "summary": "Test Ticket 1",
            "description": "Test Description 1",
            "status": "Open"
        },
        {
            "ticket_id": "DATA-2",
            "summary": "Test Ticket 2",
            "description": "Test Description 2",
            "status": "Open"
        }
    ]
    
    # Call the main function
    main("./config/config.yaml")
    
    # Assertions
    mock_jira_client_class.assert_called_once()
    mock_db_client_class.assert_called_once()
    mock_agent_class.assert_called_once()
    mock_get_active_ids.assert_called_once()
    mock_get_jira_tickets.assert_called_once()
    
    # Check that process_ticket was called twice (once for each ticket)
    assert mock_agent.process_ticket.call_count == 2