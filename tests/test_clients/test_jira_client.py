from unittest.mock import MagicMock, patch, mock_open, call
from src.clients.jira_client import JiraClient

@patch("src.clients.jira_client.requests.request")
def test_jira_client_initialization(mock_request: MagicMock):
    """Test JiraClient initialization and account ID retrieval."""
    # Mock the response from /myself
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"accountId": "test-account-id"}
    mock_request.return_value = mock_response

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token"
    )

    assert client.account_id == "test-account-id"
    mock_request.assert_called_once()
    assert client.base_url == "https://example.atlassian.net"
    assert client.auth.username == "test@example.com"


@patch.object(JiraClient, "_request")
def test_get_comments(mock_request: MagicMock) -> None:
    # Arrange
    mock_comments_data = {
        "comments": [
            {"id": "1", "body": "First comment"},
            {"id": "2", "body": "Second comment"},
        ]
    }

    mock_request.side_effect = [{"accountId": "dummy-id"}, mock_comments_data]

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )

    comments = client.get_comments(issue_key="TEST-123")
    expected_url = "https://example.atlassian.net/rest/api/2/issue/TEST-123/comment"
    mock_request.assert_any_call(method="get", url=expected_url)
    assert comments == mock_comments_data


@patch.object(JiraClient, "_request")
def test_get_issue(mock_request: MagicMock) -> None:
    """Test the get_issue method."""
    # Arrange
    mock_issue_data = {
        "key": "DATA-1",
        "fields": {
            "summary": "Test Summary",
            "description": "Test Description"
        }
    }

    mock_request.side_effect = [{"accountId": "dummy-id"}, mock_issue_data]

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )

    result = client.get_issue("DATA-1")
    expected_url = "https://example.atlassian.net/rest/api/2/issue/DATA-1"
    mock_request.assert_any_call(method="get", url=expected_url)
    assert result == mock_issue_data


@patch.object(JiraClient, "_request")
def test_update_comment(mock_request: MagicMock) -> None:
    # Arrange
    updated_comment_response = {
        "id": "12345",
        "body": "Updated comment text",
    }
    # First call to _request is from __init__ for account_id
    # Second call is the update_comment call
    mock_request.side_effect = [{"accountId": "dummy-id"}, updated_comment_response]

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )

    issue_key = "TEST-123"
    comment_id = "12345"
    new_text = "Updated comment text"

    # Act
    result = client.update_comment(issue_key=issue_key, comment_id=comment_id, new_text=new_text)

    # Assert
    expected_url = f"https://example.atlassian.net/rest/api/2/issue/{issue_key}/comment/{comment_id}"
    expected_json = {"body": new_text}

    mock_request.assert_any_call(method="put", url=expected_url, json=expected_json)
    assert result == updated_comment_response

@patch.object(JiraClient, "_request")
def test_add_comment(mock_request: MagicMock) -> None:
    # Arrange
    mock_response = {
        "id": "67890",
        "body": "This is a test comment"
    }
    # First call in __init__ to get account_id, second call is add_comment
    mock_request.side_effect = [{"accountId": "dummy-id"}, mock_response]

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )

    issue_key = "TEST-123"
    comment_text = "This is a test comment"

    # Act
    result = client.add_comment(issue=issue_key, comment=comment_text)

    # Assert
    expected_url = f"https://example.atlassian.net/rest/api/2/issue/{issue_key}/comment"
    expected_json = {"body": comment_text}

    mock_request.assert_any_call(method="post", url=expected_url, json=expected_json)
    assert result == mock_response


@patch.object(JiraClient, "_request")
def test_delete_comment(mock_request: MagicMock) -> None:
    # Arrange
    # Mock response for __init__ (account ID fetch) and delete_comment call
    mock_request.side_effect = [{"accountId": "dummy-id"}, True]

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )

    issue_key = "TEST-123"
    comment_id = "45678"

    # Act
    result = client.delete_comment(issue_key=issue_key, comment_id=comment_id)

    # Assert
    expected_url = f"https://example.atlassian.net/rest/api/2/issue/{issue_key}/comment/{comment_id}"
    mock_request.assert_any_call(method="delete", url=expected_url)
    assert result is True


@patch("requests.post")
@patch("builtins.open", new_callable=mock_open, read_data=b"dummy file content")
@patch.object(JiraClient, "_handle_response")
@patch.object(JiraClient, "_request")
def test_attach_file(mock_request, mock_handle_response, mock_file, mock_post):
    # Arrange
    # Mock _request for initialization
    def side_effect(method, url, **kwargs):
        if url.endswith("/rest/api/3/myself"):
            return {"accountId": "test-account-id"}
        return None

    mock_request.side_effect = side_effect

    # Mock _handle_response to return expected dict on file upload response
    mock_handle_response.return_value = {"id": "123", "filename": "test.txt"}

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )

    issue_key = "TEST-123"
    file_path = "test.txt"

    # Act
    result = client.attach_file(issue_key, file_path)

    # Assert
    mock_file.assert_called_once_with(file_path, "rb")
    expected_url = f"https://example.atlassian.net/rest/api/2/issue/{issue_key}/attachments"
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == expected_url
    assert "X-Atlassian-Token" in kwargs["headers"]
    assert kwargs["headers"]["X-Atlassian-Token"] == "no-check"
    assert kwargs["auth"] == client.auth
    assert "files" in kwargs
    assert result == {"id": "123", "filename": "test.txt"}




@patch.object(JiraClient, "_request")
def test_get_issue_success(mock_request):
    # Arrange
    issue_key = "TEST-123"
    expected_url = f"https://example.atlassian.net/rest/api/2/issue/{issue_key}"
    expected_response = {
        "key": issue_key,
        "fields": {
            "summary": "Test issue summary",
            "description": "Test issue description"
        }
    }

    # Setup side effects for calls to _request:
    # First call during init returns account info
    # Second call returns issue data
    mock_request.side_effect = [
        {"accountId": "some-account-id"},  # for __init__ call
        expected_response  # for get_issue call
    ]

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token"
    )

    # Act
    result = client.get_issue(issue_key)

    # Assert the calls happened as expected
    mock_request.assert_has_calls([
        call(method="get", url="https://example.atlassian.net/rest/api/3/myself"),
        call(method="get", url=expected_url),
    ])

    assert result == expected_response



@patch.object(JiraClient, "_request")
def test_create_issue_success(mock_request):
    # Arrange
    payload = {
        "summary": "Test issue",
        "description": "Test description",
        "project": {"key": "TEST"},
        "issuetype": {"name": "Bug"}
    }
    expected_url = "https://example.atlassian.net/rest/api/2/issue"
    expected_processed_fields = payload
    expected_response = {
        "id": "10001",
        "key": "TEST-1",
        "self": f"{expected_url}/10001"
    }

    # Simulate the first _request call for initialization and second for create_issue
    def side_effect(method, url, **kwargs):
        if url.endswith("/rest/api/3/myself"):
            return {"accountId": "test-account-id"}
        if url == expected_url and method == "post":
            return expected_response
        return None

    mock_request.side_effect = side_effect

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token"
    )

    mock_request.reset_mock()  # Clear previous calls during init

    with patch.object(client, "_preprocess_payload", return_value=expected_processed_fields):
        # Act
        result = client.create_issue(payload)

    # Assert
    mock_request.assert_called_once_with(
        method="post",
        url=expected_url,
        json={"fields": expected_processed_fields}
    )
    assert result == expected_response


@patch.object(JiraClient, "_request")
def test_get_active_issues_pagination(mock_request):
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token"
    )

    # Simulate 3 pages of issues: total 120 issues (50 + 50 + 20)
    issues_page_1 = [{"id": str(i)} for i in range(50)]
    issues_page_2 = [{"id": str(i)} for i in range(50, 100)]
    issues_page_3 = [{"id": str(i)} for i in range(100, 120)]

    def side_effect(method, url, params=None, **kwargs):
        start_at = params.get("startAt", 0)
        max_results = params.get("maxResults", 50)
        total = 120
        if start_at == 0:
            return {"issues": issues_page_1, "total": total}
        elif start_at == 50:
            return {"issues": issues_page_2, "total": total}
        elif start_at == 100:
            return {"issues": issues_page_3, "total": total}
        return {"issues": [], "total": total}

    mock_request.side_effect = side_effect

    # Act: fetch all issues with limit=-1 (default)
    result = client.get_active_issues()

    # Assert
    assert len(result) == 120
    assert result[0]["id"] == "0"
    assert result[-1]["id"] == "119"


@patch.object(JiraClient, "_request")
def test_update_issue_success(mock_request):
    # Mock the init call (to avoid actual requests)
    mock_request.return_value = {"accountId": "test-account-id"}

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token"
    )

    # Now reset mock to clear init call history
    mock_request.reset_mock()

    issue_key = "TEST-123"
    update_fields = {
        "summary": "Fix broken login form",
        "description": "This bug occurs on mobile Safari browsers.",
        "priority": {"name": "Critical"},
        "assignee": {"accountId": "abcd1234"},
        "duedate": "2025-06-30"
    }

    expected_url = f"https://example.atlassian.net/rest/api/2/issue/{issue_key}"
    expected_json = {"fields": update_fields}
    expected_response = {"key": issue_key, "fields": update_fields}
    mock_request.return_value = expected_response

    result = client.update_issue(issue_key, update_fields)

    mock_request.assert_called_once_with(method="put", url=expected_url, json=expected_json)
    assert result == expected_response


@patch.object(JiraClient, "_request")
def test_get_available_transitions_success(mock_request):
    # Arrange
    issue_key = "TEST-123"
    expected_url = f"https://example.atlassian.net/rest/api/2/issue/{issue_key}/transitions"
    mock_response = {
        "transitions": [
            {"id": "11", "name": "Start Progress"},
            {"id": "21", "name": "Resolve Issue"},
        ]
    }
    mock_request.return_value = mock_response

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token"
    )

    # Act
    result = client.get_available_transitions(issue_key)

    # Assert
    mock_request.assert_called_with(method="get", url=expected_url)
    assert result == mock_response["transitions"]


@patch.object(JiraClient, "_request")
@patch.object(JiraClient, "get_available_transitions")
def test_transition_issue_success(mock_get_transitions, mock_request):
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token"
    )

    issue_key = "TEST-123"
    status_name = "In Progress"

    # Mock available transitions
    mock_get_transitions.return_value = [
        {"id": "11", "name": "To Do"},
        {"id": "21", "name": "In Progress"},
        {"id": "31", "name": "Done"},
    ]

    # Mock the _request to return a success dict
    expected_response = {"transitioned": True}
    mock_request.return_value = expected_response

    result = client.transition_issue(issue_key, status_name)

    mock_get_transitions.assert_called_once_with(issue_key=issue_key)

    expected_url = f"https://example.atlassian.net/rest/api/2/issue/{issue_key}/transitions"
    expected_json = {"transition": {"id": "21"}}

    # Instead of assert_called_once_with, check that call is present among calls:
    mock_request.assert_any_call(method="post", url=expected_url, json=expected_json)

    assert result == expected_response

@patch.object(JiraClient, "_request")
def test_search_issues_pagination(mock_request):
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token"
    )

    jql = "project = TEST ORDER BY created DESC"
    max_results = 150  # More than one batch of 100

    first_batch = {
        "issues": [{"id": str(i)} for i in range(100)],
        "total": 150,
    }
    second_batch = {
        "issues": [{"id": str(i)} for i in range(100, 150)],
        "total": 150,
    }

    # Clear any previous side effects caused by __init__ calls
    mock_request.reset_mock()
    # Now setup side_effect for only search_issues pagination calls
    mock_request.side_effect = [first_batch, second_batch]

    result = client.search_issues(jql, max_results=max_results)

    assert "issues" in result
    assert len(result["issues"]) == max_results
    assert result["issues"][0]["id"] == "0"
    assert result["issues"][-1]["id"] == "149"

    assert mock_request.call_count == 2

    # Optionally check params of calls
    first_call_params = mock_request.call_args_list[0].kwargs
    second_call_params = mock_request.call_args_list[1].kwargs

    assert first_call_params["method"] == "get"
    assert first_call_params["params"]["maxResults"] == 100
    assert first_call_params["params"]["startAt"] == 0

    assert second_call_params["method"] == "get"
    assert second_call_params["params"]["maxResults"] == 50
    assert second_call_params["params"]["startAt"] == 100


@patch.object(JiraClient, "_request", return_value={"accountId": "dummy-account-id"})
def test_extract_issue_details_with_string_description(mock_request):
    client = JiraClient(base_url="https://example.atlassian.net", email="test@example.com", api_token="token")

    # Provide simple _safe_get implementation
    client._safe_get = lambda d, key, subkey: d.get(key, {}).get(subkey) if d.get(key) else None

    issue = {
        "key": "TEST-123",
        "fields": {
            "summary": "Test issue summary",
            "description": "Simple description string",
            "status": {"name": "Open"},
            "assignee": {
                "accountId": "acc-1",
                "displayName": "John Doe",
                "emailAddress": "john@example.com",
            },
            "reporter": {
                "accountId": "acc-2",
                "displayName": "Jane Smith",
                "emailAddress": "jane@example.com",
            },
            "priority": {"name": "High"},
            "duedate": "2025-06-30",
            "created": "2025-01-01T12:00:00.000+0000",
            "updated": "2025-01-02T15:00:00.000+0000",
        }
    }

    details = client.extract_issue_details(issue)

    assert details["ticket_id"] == "TEST-123"
    assert details["summary"] == "Test issue summary"
    assert details["description"] == "Simple description string"
    assert details["status"] == "Open"
    assert details["assignee"]["account_id"] == "acc-1"
    assert details["assignee"]["name"] == "John Doe"
    assert details["assignee"]["email"] == "john@example.com"
    assert details["reporter"]["account_id"] == "acc-2"
    assert details["reporter"]["name"] == "Jane Smith"
    assert details["reporter"]["email"] == "jane@example.com"
    assert details["priority"] == "High"
    assert details["due_date"] == "2025-06-30"
    assert details["created_date"] == "2025-01-01T12:00:00.000+0000"
    assert details["updated_date"] == "2025-01-02T15:00:00.000+0000"