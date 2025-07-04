from unittest.mock import patch, MagicMock
from src.tools.insight_tool import InsightTool
from src.models.schemas import QueryResult


def test_insight_tool_initialization() -> None:
    """Test the initialization of the InsightTool."""
    mock_llm = MagicMock()
    tool = InsightTool(llm=mock_llm)
    assert tool.llm == mock_llm


def test_format_result_summary() -> None:
    """Test formatting the result summary."""
    mock_llm = MagicMock()
    query_result = QueryResult(
        data=[{"col1": "val1", "col2": "val2"}],
        row_count=1,
        column_names=["col1", "col2"],
        execution_time_ms=10
    )
    tool = InsightTool(llm=mock_llm)
    summary = tool.format_result_summary(query_result)
    assert "col1" in summary
    assert "col2" in summary
    assert "val1" in summary
    assert "val2" in summary
    assert "Total rows: 1" in summary  # Matches your implementation's wording


@patch("src.tools.insight_tool.logger")
def test_generate_insights_success(mock_logger) -> None:
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="This is a test insight.")

    query_result = QueryResult(
        data=[{"col1": "val1", "col2": "val2"}],
        row_count=1,
        column_names=["col1", "col2"],
        execution_time_ms=10,
    )

    tool = InsightTool(llm=mock_llm)
    insight_text = tool.generate_insights("Analyze col1 and col2", query_result)

    assert insight_text == "This is a test insight."
    mock_llm.invoke.assert_called_once()
    mock_logger.info.assert_called()  # Now this should work correctly
