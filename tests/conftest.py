import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_jira_client() -> MagicMock:
    client = MagicMock()
    client.get_active_issues.return_value = [{"key": "DATA-1"}, {"key": "DATA-2"}]
    client.account_id = "bot_account_id"
    return client

@pytest.fixture
def sample_issue_comments_empty() -> dict:
    return {"comments": []}

@pytest.fixture
def sample_issue_comments_with_bot_last() -> dict:
    return {
        "comments": [
            {"author": {"accountId": "user123"}},
            {"author": {"accountId": "bot_account_id"}},
        ]
    }

@pytest.fixture
def sample_issue_comments_with_user_last() -> dict:
    return {
        "comments": [
            {"author": {"accountId": "bot_account_id"}},
            {"author": {"accountId": "user456"}},
        ]
    }
