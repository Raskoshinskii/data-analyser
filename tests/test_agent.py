import pytest
from unittest.mock import patch, MagicMock

from src.agent.agent import DataAnalysisAgent


@patch('src.agent.agent.workflow.build')
@patch('src.agent.agent.SQLTool')
@patch('src.agent.agent.ValidatorTool')
@patch('src.agent.agent.InsightTool')
def test_agent_initialization(mock_insight_tool, mock_validator_tool, 
                             mock_sql_tool, mock_workflow_build, mock_db_client):
    """Test the initialization of the DataAnalysisAgent."""
    # Create the agent
    agent = DataAnalysisAgent(agent_config="./config/config.yaml", db_client=mock_db_client)
    
    # Assertions
    assert agent.db_client == mock_db_client
    assert agent.max_retries == 3  # default value
    mock_workflow_build.assert_called_once()
    mock_sql_tool.assert_called_once()
    mock_validator_tool.assert_called_once()
    mock_insight_tool.assert_called_once()


@patch('src.agent.agent.workflow.build')
@patch('src.agent.agent.SQLTool')
@patch('src.agent.agent.ValidatorTool')
@patch('src.agent.agent.InsightTool')
def test_process_ticket(mock_insight_tool, mock_validator_tool, 
                       mock_sql_tool, mock_workflow_build, mock_db_client, sample_jira_ticket):
    """Test processing a ticket."""
    # Setup
    mock_workflow = MagicMock()
    mock_workflow_build.return_value = mock_workflow
    
    # Create the agent
    agent = DataAnalysisAgent(agent_config="./config/config.yaml", db_client=mock_db_client)
    
    # Process a ticket
    agent.process_ticket(sample_jira_ticket)
    
    # Assertions
    mock_workflow.assert_called_once()
    # Check that the workflow was called with the correct state
    args, _ = mock_workflow.call_args
    initial_state = args[0]
    assert initial_state.ticket == sample_jira_ticket
    assert initial_state.current_task is None
    assert initial_state.sql_query is None