import sys
from pathlib import Path
from typing import Any, Dict, List
from typing import MagicMock as MagicMockType
from unittest.mock import MagicMock

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.models.schemas import JiraTicket, QueryResult


@pytest.fixture
def mock_jira_client() -> MagicMockType:
    """Create a mock JIRA client."""
    mock_client = MagicMock()
    mock_client.account_id = "test-account-id"

    # Mock the get_active_issues method
    mock_client.get_active_issues.return_value = [{"key": "DATA-1"}, {"key": "DATA-2"}]

    # Mock the get_comments method
    mock_client.get_comments.return_value = {
        "comments": [{"author": {"accountId": "not-the-bot-id"}}]
    }

    # Mock the get_issue method
    mock_client.get_issue.return_value = {"key": "DATA-1"}

    # Mock the extract_issue_details method
    mock_client.extract_issue_details.return_value = {
        "ticket_id": "DATA-1",
        "summary": "Test Ticket",
        "description": "Test Description",
        "status": "Open",
    }

    return mock_client


@pytest.fixture
def mock_db_client() -> MagicMockType:
    """Create a mock database client."""
    mock_client = MagicMock()

    # Mock the execute_query method
    mock_client.execute_query.return_value = QueryResult(
        data=[{"column1": "value1"}],
        row_count=1,
        column_names=["column1"],
        execution_time_ms=10,
    )

    # Mock the get_tables method
    mock_client.get_tables.return_value = ["models", "sales", "dealerships"]

    # Mock the get_schema method
    mock_client.get_schema.return_value = {
        "models": [
            {"column_name": "model_id", "data_type": "INTEGER"},
            {"column_name": "model_name", "data_type": "TEXT"},
        ]
    }

    return mock_client


@pytest.fixture
def mock_agent() -> MagicMockType:
    """Create a mock agent."""
    mock_agent = MagicMock()
    mock_agent.process_ticket.return_value = "Success"
    return mock_agent


@pytest.fixture
def sample_jira_ticket() -> JiraTicket:
    """Create a sample JIRA ticket."""
    return JiraTicket(
        ticket_id="DATA-1",
        summary="Car Models Analysis",
        description="How many unique car models do we have per car category?",
        status="Open",
    )


@pytest.fixture
def sample_active_issues() -> List[Dict[str, str]]:
    """Sample active issues."""
    return [{"key": "DATA-1"}, {"key": "DATA-2"}, {"key": "DATA-3"}]


@pytest.fixture
def sample_issue_comments_empty() -> Dict[str, List]:
    """Sample empty issue comments."""
    return {"comments": []}


@pytest.fixture
def sample_issue_comments_with_bot_last() -> Dict[str, List[Dict[str, Any]]]:
    """Sample issue comments with bot as last commenter."""
    return {
        "comments": [
            {"author": {"accountId": "user-id"}},
            {"author": {"accountId": "test-account-id"}},
        ]
    }


@pytest.fixture
def sample_issue_comments_with_user_last() -> Dict[str, List[Dict[str, Any]]]:
    """Sample issue comments with user as last commenter."""
    return {
        "comments": [
            {"author": {"accountId": "test-account-id"}},
            {"author": {"accountId": "user-id"}},
        ]
    }
