from unittest.mock import MagicMock, patch
from src.agent.agent import DataAnalysisAgent
from src.models.schemas import JiraTicket



import pytest
from unittest.mock import MagicMock, patch
from src.agent.agent import DataAnalysisAgent
from src.models.schemas import JiraTicket, AgentState


@pytest.fixture
def sample_jira_ticket():
    return JiraTicket(
        ticket_id="ABC-123",
        summary="Analyze sales",
        description="Analyze sales data for Q2 by region",
        status="Open"  # or whatever enum/string your model expects
    )

@patch("src.agent.agent.create_workflow")
@patch("src.agent.agent.SQLTool")
@patch("src.agent.agent.ValidatorTool")
@patch("src.agent.agent.InsightTool")
@patch("src.agent.agent.ChatOpenAI")
@patch("src.agent.agent.JiraClient")
def test_agent_initialization(
    mock_jira_client,
    mock_chat_openai,
    mock_insight_tool,
    mock_validator_tool,
    mock_sql_tool,
    mock_create_workflow,
    mock_db_client,
):
    """Test the initialization of the DataAnalysisAgent."""
    mock_db_client.get_database_schema.return_value = {"table1": []}
    mock_create_workflow.return_value = MagicMock()

    agent = DataAnalysisAgent(
        agent_config="./config/config.yaml", db_client=mock_db_client
    )

    assert agent.db_client == mock_db_client
    assert agent.max_retries == 3
    mock_create_workflow.assert_called_once()
    mock_sql_tool.assert_called_once()
    mock_validator_tool.assert_called_once()
    mock_insight_tool.assert_called_once()
    mock_chat_openai.assert_called_once()
    mock_jira_client.assert_called_once()


@patch("src.agent.agent.create_workflow")
@patch("src.agent.agent.SQLTool")
@patch("src.agent.agent.ValidatorTool")
@patch("src.agent.agent.InsightTool")
@patch("src.agent.agent.ChatOpenAI")
@patch("src.agent.agent.JiraClient")
def test_process_ticket(
    mock_jira_client,
    mock_chat_openai,
    mock_insight_tool,
    mock_validator_tool,
    mock_sql_tool,
    mock_create_workflow,
    mock_db_client,
    sample_jira_ticket,
):
    """Test processing a JIRA ticket end-to-end."""
    mock_db_client.get_database_schema.return_value = {"table1": []}
    mock_final_state = AgentState(ticket=sample_jira_ticket, business_insight="Some insight")
    mock_workflow = MagicMock()
    mock_workflow.invoke.return_value = mock_final_state
    mock_create_workflow.return_value = mock_workflow

    agent = DataAnalysisAgent(
        agent_config="./config/config.yaml", db_client=mock_db_client
    )

    agent.process_ticket(sample_jira_ticket)

    mock_workflow.invoke.assert_called_once()
    args, _ = mock_workflow.invoke.call_args
    passed_state = args[0]
    assert passed_state.ticket == sample_jira_ticket
