import json
import copy
import logging
import requests

from typing import Any, Dict, List, Optional, Union
from requests.auth import HTTPBasicAuth

# from src.models.schemas import JiraTicket, TicketStatus, BusinessInsight

logger = logging.getLogger(__name__)


class JiraClient:
    def __init__(self, *, base_url: str, api_token: str, email: str) -> None:
        """
        Initialize the JiraClient with authentication and base URL setup.

        Parameters
        ----------
        base_url : str
            The base URL of the Jira instance.
        api_token : str
            The API token for authenticating with Jira.
        email : str
            The email address associated with the Jira account.
        """
        self.email = email
        self.api_token = self._fix_api_token(api_token)
        self.base_url = self._fix_base_url(base_url)
        self.auth = HTTPBasicAuth(username=self.email, password=self.api_token)
        self.headers = {"Content-Type": "application/json"}
        self.account_id = self._get_account_id()

    def _fix_api_token(self, api_token: str) -> str:
        """
        Strip 'Bearer' prefix from the API token if present.

        Parameters
        ----------
        api_token : str
            The API token generted in "Atlassian", potentially prefixed with 'Bearer'.

        Returns
        -------
        str
            The cleaned API token.
        """
        if api_token.startswith("Bearer "):
            api_token = api_token.split("Bearer ")[-1]
        return api_token

    def _fix_base_url(self, base_url: str) -> str:
        """
        Normalize the base URL to ensure it has no trailing slash and has a protocol.

        Parameters
        ----------
        base_url : str
            The raw base URL input.

        Returns
        -------
        str
            The fixed and normalized base URL.
        """
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        if not base_url.startswith("http"):
            base_url = f"http://{base_url}"
        return base_url

    def _handle_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """
        Handle the HTTP response from Jira API calls.

        Parameters
        ----------
        response : requests.Response
            The response object returned from a requests call.

        Returns
        -------
        Optional[Dict[str, Any]]
            The parsed JSON response if successful, otherwise raises an exception.
        """
        if response.status_code in (200, 201):
            return response.json()
        elif response.status_code == 401:
            raise PermissionError(
                "Unauthorized access. Please check your API token and email."
            )
        elif response.status_code == 403:
            raise PermissionError(
                "Forbidden access. You do not have permission to perform this action."
            )
        elif response.status_code == 404:
            raise ValueError(
                "Resource not found. Please check the provided identifier."
            )
        elif response.status_code == 400:
            content = json.loads(response.content.decode("utf-8"))
            error = content.get("errors", content)
            raise ValueError(
                f"Bad Request. Please check the request payload! Error: {error}"
            )
        else:
            response.raise_for_status()

    def _safe_get(self, d, *keys) -> Optional[Dict[str, Any]]:
        """
        Utility to safely traverse nested dictionaries.

        Parameters
        ----------
        d : dict
            The dictionary to traverse.
        *keys : str
            A sequence of keys to follow in the nested dictionary.

        Returns
        -------
        Optional[Any]
            The value at the nested key path if all keys exist, otherwise None.
        """
        for key in keys:
            if not d:
                return None
            d = d.get(key)
        return d

    def _extract_text_from_adf(self, adf_content: Union[Dict[str, Any], list]) -> str:
        """
        Utility to recursively extract plain text from "Atlassian Document Format" (ADF).

        Parameters
        ----------
        adf_content : Union[dict, list]
            The ADF content structure, either a dictionary or a list of nested dictionaries/lists.

        Returns
        -------
        str
            Concatenated plain text extracted from the ADF structure.
        """
        if isinstance(adf_content, list):
            return " ".join(self._extract_text_from_adf(c) for c in adf_content)
        elif isinstance(adf_content, dict):
            if adf_content.get("type") == "text":
                return adf_content.get("text", "")
            elif "content" in adf_content:
                return self._extract_text_from_adf(adf_content["content"])
        return ""

    def _request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Send an HTTP request using the specified method and URL, along with optional parameters.

        Parameters
        ----------
            method: str
                The HTTP method to use (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            url: str
                The full URL to send the request to.
            **kwargs:
                Optional arguments passed directly to `requests.request` (e.g., json, params, data, timeout).

        Returns
        -------
            Dict[str, Any]
                The parsed JSON response or processed output from the server.
        """
        response = requests.request(
            method=method, url=url, headers=self.headers, auth=self.auth, **kwargs
        )
        return self._handle_response(response)
    
    def _preprocess_payload(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aligns the payload structure with Jira API requirements.

        Important
        ---------
        - The function covers the most common fileds of a payload. 
        New fields should be either included in the function or formatted in the payload!
        - Performs "inplace" operation! 
        
        Parameters
        ----------
        payload : Dict[str, Any]
            The raw payload dictionary containing issue data.

        Returns
        -------
        Dict[str, Any]
            The processed payload with 'fields' key and proper structure.
        """
        if isinstance(payload.get("project"), str):
            payload["project"] = {"key": payload["project"]}

        if isinstance(payload.get("issuetype"), str):
            payload["issuetype"] = {"name": payload["issuetype"]}

        if isinstance(payload.get("components"), str):
            payload["components"] = [{"name": payload["components"]}]

        if isinstance(payload.get("assignee"), str):
            payload["assignee"] = [{"accountId": payload["assignee"]}]

        if isinstance(payload.get("assignee"), str):
            payload["reporteer"] = [{"accountId": payload["reporteer"]}]

        return payload
    
    def _get_account_id(self) -> str | None:
        """
        Get the account ID of the currently authenticated user.

        Returns
        -------
        str
            The account ID of the authenticated user.
        """
        url = f"{self.base_url}/rest/api/3/myself"
        response = self._request(method="get", url=url)
        
        if not response or "accountId" not in response:
            return None
            
        return response.get("accountId")

    def get_comments(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve all comments for a Jira issue.

        Parameters
        ----------
        issue_key : str
            The key of the issue to retrieve comments from (e.g. "VWNPER-1", "BIO-2", etc).

        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing comments data if successful.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
        return self._request(method="get", url=url)

    def update_comment(
        self, issue_key: str, comment_id: str, new_text: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing comment on a Jira issue.

        Parameters
        ----------
        issue_key : str
            The key of the issue containing the comment (e.g. "VWNPER-1", "BIO-2", etc).
        comment_id : str
            The ID of the comment to update.
        new_text : str
            The updated comment body.

        Returns
        -------
        Optional[Dict[str, Any]]
            The updated comment data if successful.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment/{comment_id}"
        json = {"body": new_text}
        return self._request(method="put", url=url, json=json)

    def add_comment(self, issue: str, comment: str) -> Optional[Dict[str, Any]]:
        """
        Add a comment to a specific Jira issue.

        Parameters
        ----------
        issue : str
            The key or ID of the issue to comment on (e.g. "VWNPER-1", "BIO-2", etc).
        comment : str
            The content of the comment to add.

        Returns
        -------
        Optional[Dict[str, Any]]
            The API response as a dictionary if successful.
        """
        api_endpoint = f"rest/api/2/issue/{issue}/comment"
        url = f"{self.base_url}/{api_endpoint}"
        json = {"body": comment}
        return self._request(method="post", url=url, json=json)

    def delete_comment(
        self, issue_key: str, comment_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Delete a comment from a Jira issue.

        Parameters
        ----------
        issue_key : str
            The key of the issue containing the comment (e.g. "VWNPER-1").
        comment_id : str
            The ID of the comment to delete.

        Returns
        -------
        bool
            True if the comment was successfully deleted, False otherwise.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment/{comment_id}"
        return self._request(method="delete", url=url)

    def attach_file(self, issue_key: str, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Attach a file to a Jira issue. Attachments are always linked to the issue itself.

        Parameters
        ----------
        issue_key : str
            The key of the issue.
        file_path : str
            Path to the file to upload.

        Returns
        -------
        Optional[Dict[str, Any]]
            Attachment metadata if successful.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/attachments"

        # Remove content-type if it's in self.headers
        headers = {k: v for k, v in self.headers.items() if k.lower() != "content-type"}
        headers["X-Atlassian-Token"] = "no-check"

        with open(file_path, "rb") as file:
            files = {"file": (file_path, file)}
            response = requests.post(url, headers=headers, auth=self.auth, files=files)
        return self._handle_response(response)

    def get_issue(self, issue: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve details of a specific Jira issue.

        Parameters
        ----------
        issue : str
            The key or ID of the issue to retrieve (e.g. "VWNPER-1", "BIO-2", etc).

        Returns
        -------
        Optional[Dict[str, Any]]
            The issue data as a dictionary if found.
        """
        api_endpoint = f"rest/api/2/issue/{issue}"
        url = f"{self.base_url}/{api_endpoint}"
        return self._request(method="get", url=url)

    def create_issue(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a new Jira issue with required and optional fields.

        Parameters
        ----------
        payload : Dict[str, Any]
            A dictionary containing the issue data.

        Returns
        -------
        Optional[Dict[str, Any]]
            Created issue data if successful.
        """
        api_endpoint = "rest/api/2/issue"
        url = f"{self.base_url}/{api_endpoint}"
        fields = self._preprocess_payload(payload)
        
        return self._request(method="post", url=url, json={"fields": fields})

    def get_active_issues(
        self, limit: int = -1, start_at: int = 0, batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve issues assigned to the current user that are not marked as 'Done'.

        Parameters
        ----------
        limit: int
            The maximum number of issues to retrieve. If set to -1 (default), retrieves
            all matching issues using pagination.
        start_at: int
            The index of the first issue to return. This is useful to keep track of
            retrieved issues. So that we don't retreieve the same issues again.
        batch_size: int
            The maximum number of issues to fetch per request (max allowed by Jira is 100)

        Returns
        -------
            List[Dict[str, Any]]: A list of dictionaries represention the retrieved issues.
        """
        api_endpoint = "rest/api/3/search"
        url = f"{self.base_url}/{api_endpoint}"
        jql = "assignee=currentUser() AND statusCategory != Done ORDER BY created DESC"

        # container for accumulated issues
        all_issues = []

        while True:
            # determine how many issues to fetch for the first iteration
            if limit == -1:
                current_max = batch_size
            else:
                current_max = min(limit - len(all_issues), batch_size)

            if current_max <= 0:
                break

            params = {
                "jql": jql,
                "maxResults": current_max,
                "startAt": start_at,
            }

            # request a batch of issues
            result = self._request(method="get", url=url, params=params)

            if not result or "issues" not in result:
                break

            issues = result["issues"]
            all_issues.extend(issues)

            if limit != -1 and len(all_issues) >= limit:
                break

            if start_at + len(issues) >= result.get("total", 0):
                break

            start_at += len(issues)

        return all_issues

    def update_issue(
        self, issue_key: str, fields: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update fields of a Jira issue. Not all fields can be updated.
        Full list depends on Jira configuration. Here are most commonly updated fields:
            - "Summary": ticket title.
            - "Description": detailed description of the ticket.
            - "Priority": ticket priority.
            - "Assignee": assignee name.
            - "Duedate": ticket due date.

        Parameters
        ----------
        issue_key : str
            The key of the issue to update (e.g. "VWNPER-1", "BIO-2", etc).
        fields : Dict[str, Any]
            A dictionary of fields to update. For example:
            fields = {
                "summary": "Fix broken login form",
                "description": "This bug occurs on mobile Safari browsers.",
                "priority": {"name": "Critical"},
                "assignee": {"accountId": "abcd1234"},
                "duedate": "2025-06-30"
            }

            Name of the priorites should be one of the following and starts with capital letter:
                - "Blocker"
                - "Critical"
                - "Major"
                - "Minor"
                - "Trivial"

        Returns
        -------
        Optional[Dict[str, Any]]
            The updated issue data if successful.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
        return self._request(method="put", url=url, json={"fields": fields})

    def get_available_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Retrieve all possible transitions for the given issue.

        Parameters
        ----------
        issue_key : str
            The Jira issue key (e.g. "VWNPER-1", "BIO-2", etc).

        Returns
        -------
        list[dict]
            A list of transition objects, each containing 'id' and 'name'.
        """
        url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
        data = self._request(method="get", url=url)
        assert isinstance(data, dict)
        return data.get("transitions", [])

    def transition_issue(
        self, issue_key: str, status_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Transition the issue to a new status by name.

        Parameters
        ----------
        issue_key : str
            The Jira issue key (e.g. "VWNPER-1", "BIO-2", etc).
        status_name : str
            The desired status to transition to (e.g., "In Progress", "Close Issue", etc).

        Returns
        -------
        Optional[Dict[str, Any]]
            The result of the transition if successful.
        """
        # get available transitions
        transitions = self.get_available_transitions(issue_key=issue_key)

        if not transitions:
            raise ValueError("No transitions found for this issue.")

        # find the transition ID for the given status name
        matching = [t for t in transitions if t["name"].lower() == status_name.lower()]
        if not matching:
            raise ValueError(f"Transition to '{status_name}' not available.")

        transition_id = matching[0]["id"]

        # perform the transition
        transition_url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
        data = {"transition": {"id": transition_id}}
        return self._request(method="post", url=transition_url, json=data)

    def search_issues(self, jql: str, max_results: int = 50) -> Dict[str, Any]:
        """
        Search Jira issues using JQL. Jira limits number of results per request to 100.

        Parameters
        ----------
        jql : str
            Jira Query Language string.
        max_results : int
            Maximum number of results to return. If -1, fetches all matching issues.

        Returns
        -------
        Optional[Dict[str, Any]]
            The search results.
        """
        all_issues = []
        start_at = 0
        batch_size = 100

        # "pagination logic" to be able to retrieve more than 100 issues
        while True:
            if max_results == -1:
                batch_limit = batch_size
            else:
                batch_limit = min(batch_size, max_results - len(all_issues))
                if batch_limit <= 0:
                    break

            url = f"{self.base_url}/rest/api/2/search"
            params = {"jql": jql, "maxResults": batch_limit, "startAt": start_at}

            result = self._request(method="get", url=url, params=params)

            if not result or "issues" not in result:
                break

            issues = result["issues"]
            all_issues.extend(issues)

            if max_results != -1 and len(all_issues) >= max_results:
                break

            if start_at + len(issues) >= result.get("total", 0):
                break

            start_at += len(issues)

        return {"issues": all_issues}

    def extract_issue_details(self, issue: dict) -> Dict[str, Any]:
        """
        Extract detailed info from a Jira issue JSON.

        Parameters
        ----------
        issue : dict
            The Jira issue JSON object as returned by get_issue function.

        Returns
        -------
        dict
            Fileds of interest from the issue JSON.
        """
        fields = issue.get("fields", {})
        description_field = fields.get("description")
        description_text = ""

        if isinstance(description_field, str):
            description_text = description_field
        elif isinstance(description_field, dict):
            description_text = self._extract_text_from_adf(
                description_field.get("content", [])
            )

        return {
            "ticket_id": issue.get("key"),
            "summary": fields.get("summary"),
            "description": description_text.strip() if description_text else None,
            "status": self._safe_get(fields, "status", "name"),
            "assignee": {
                "account_id": self._safe_get(fields, "assignee", "accountId"),
                "name": self._safe_get(fields, "assignee", "displayName"),
                "email": self._safe_get(fields, "assignee", "emailAddress"),
            },
            "reporter": {
                "account_id": self._safe_get(fields, "reporter", "accountId"),
                "name": self._safe_get(fields, "reporter", "displayName"),
                "email": self._safe_get(fields, "reporter", "emailAddress"),
            },
            "priority": self._safe_get(fields, "priority", "name"),
            "due_date": fields.get("duedate"),
            "created_date": fields.get("created"),
            "updated_date": fields.get("updated"),
        }
