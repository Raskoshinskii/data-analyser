from typing import Any, Dict, List
from unittest.mock import MagicMock, patch
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import get_active_issue_ids_from_jira, get_jira_tickets

@pytest.fixture
def mock_jira_client() -> MagicMock:
    client = MagicMock()
    client.get_active_issues.return_value = [{"key": "DATA-1"}, {"key": "DATA-2"}]
    client.account_id = "bot_account_id"
    return client


def test_get_jira_tickets(mock_jira_client: MagicMock) -> None:
    mock_jira_client.get_issue.return_value = MagicMock()
    mock_jira_client.extract_issue_details.side_effect = [
        {
            "ticket_id": "DATA-1",
            "summary": "Test Ticket",
            "description": "Desc 1",
            "status": "Open",
        },
        {
            "ticket_id": "DATA-2",
            "summary": "Test Ticket",
            "description": "Desc 2",
            "status": "Open",
        },
    ]

    with patch("main.get_active_issue_ids_from_jira", return_value=["DATA-1", "DATA-2"]):
        result = get_jira_tickets(mock_jira_client, ["DATA-1", "DATA-2"])

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["ticket_id"] == "DATA-1"
    assert result[0]["summary"] == "Test Ticket"
