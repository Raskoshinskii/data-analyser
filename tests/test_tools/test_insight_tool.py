from unittest.mock import patch, MagicMock
from src.tools.insight_tool import InsightTool
from src.models.schemas import QueryResult, BusinessInsight


@patch('src.tools.insight_tool.ChatOpenAI')
def test_insight_tool_initialization(mock_chat_openai: MagicMock) -> None:
    """Test the initialization of the InsightTool."""
    # Setup
    mock_llm = MagicMock()
    
    # Create the tool
    tool = InsightTool(llm=mock_llm)
    
    # Assertions
    assert tool.llm == mock_llm


@patch('src.tools.insight_tool.ChatOpenAI')
def test_format_result_summary(mock_chat_openai: MagicMock) -> None:
    """Test formatting the result summary."""
    # Setup
    mock_llm = MagicMock()
    
    query_result = QueryResult(
        data=[{"col1": "val1", "col2": "val2"}],
        row_count=1,
        column_names=["col1", "col2"],
        execution_time_ms=10
    )
    
    # Create the tool
    tool = InsightTool(llm=mock_llm)
    
    # Format result summary
    summary = tool.format_result_summary(query_result)
    
    # Assertions
    assert "col1" in summary
    assert "col2" in summary
    assert "val1" in summary
    assert "val2" in summary
    assert "1 row" in summary


@patch('src.tools.insight_tool.ChatOpenAI')
def test_generate_insights(mock_chat_openai: MagicMock) -> None:
    """Test generating insights."""
    # Setup
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "This is a test insight."
    
    query_result = QueryResult(
        data=[{"col1": "val1", "col2": "val2"}],
        row_count=1,
        column_names=["col1", "col2"],
        execution_time_ms=10
    )
    
    # Create the tool
    tool = InsightTool(llm=mock_llm)
    
    # Generate insights
    insights = tool.generate_insights(
        task_description="Analyze col1 and col2",
        query_result=query_result
    )
    
    # Assertions
    assert isinstance(insights, BusinessInsight)
    assert insights.insight == "This is a test insight."
    mock_llm.invoke.assert_called_once()


@patch('src.tools.insight_tool.ChatOpenAI')
def test_generate_insights_empty_result(mock_chat_openai: MagicMock) -> None:
    """Test generating insights with empty result."""
    # Setup
    mock_llm = MagicMock()
    
    query_result = QueryResult(
        data=[],
        row_count=0,
        column_names=["col1", "col2"],
        execution_time_ms=10
    )
    
    # Create the tool
    tool = InsightTool(llm=mock_llm)
    
    # Generate insights
    insights = tool.generate_insights(
        task_description="Analyze col1 and col2",
        query_result=query_result
    )
    
    # Assertions
    assert isinstance(insights, BusinessInsight)
    assert "No data found" in insights.insight
    # LLM should not be called when there's no data
    mock_llm.invoke.assert_not_called()