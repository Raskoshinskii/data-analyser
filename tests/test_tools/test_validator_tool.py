from unittest.mock import MagicMock, patch
from src.models.schemas import ValidationResult
from src.tools.validator_tool import ValidatorTool


def test_validator_tool_initialization() -> None:
    """Test the initialization of the ValidatorTool."""
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    assert tool.llm == mock_llm
    assert tool.schema_dict == schema_dict


@patch("src.tools.validator_tool.sqlvalidator.parse")
def test_check_syntax_valid(mock_parse: MagicMock) -> None:
    """Test checking syntax with valid SQL."""
    mock_parse.return_value.is_valid.return_value = True

    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    is_valid, error = tool.check_syntax("SELECT * FROM table1")

    assert is_valid is True
    assert error is None
    mock_parse.assert_called_once_with("SELECT * FROM table1")


@patch("src.tools.validator_tool.sqlvalidator.parse")
def test_check_syntax_invalid(mock_parse: MagicMock) -> None:
    """Test checking syntax with invalid SQL."""
    mock_parse.return_value.is_valid.return_value = False

    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    is_valid, error = tool.check_syntax("SELEC * FRUM table1")

    assert is_valid is False
    assert error == "Invalid Syntax"
    mock_parse.assert_called_once_with("SELEC * FRUM table1")


def test_check_dangerous_patterns_safe() -> None:
    """Test checking for dangerous patterns with safe SQL."""
    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    is_safe, error = tool.check_dangerous_patterns("SELECT * FROM table1")

    assert is_safe is True
    assert error is None


def test_check_dangerous_patterns_unsafe() -> None:
    """Test checking for dangerous patterns with unsafe SQL."""
    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    is_safe, error = tool.check_dangerous_patterns("DROP TABLE table1")

    assert is_safe is False
    assert "DROP" in error


@patch("src.tools.validator_tool.Parser")
def test_check_schema_compatibility_valid(mock_parser: MagicMock) -> None:
    """Test checking schema compatibility with valid SQL."""
    mock_instance = MagicMock()
    mock_instance.tables = ["table1"]
    mock_instance.columns = ["col1"]

    # Both Parser calls return the same instance
    mock_parser.side_effect = [mock_instance, mock_instance]

    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    is_compatible, error = tool.check_schema_compatibility("SELECT col1 FROM table1")

    assert is_compatible is True
    assert error is None

    # Called twice, each with the same argument
    assert mock_parser.call_count == 2
    mock_parser.assert_any_call("SELECT col1 FROM table1")


@patch("src.tools.validator_tool.Parser")
def test_check_schema_compatibility_invalid_table(mock_parser: MagicMock) -> None:
    """Test schema compatibility with invalid table."""
    mock_instance = MagicMock()
    mock_instance.tables = ["nonexistent_table"]
    mock_instance.columns = ["col1"]

    # Return same mock instance for both calls to Parser
    mock_parser.side_effect = [mock_instance, mock_instance]

    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    is_compatible, error = tool.check_schema_compatibility("SELECT col1 FROM nonexistent_table")

    assert is_compatible is False
    assert "nonexistent_table" in error

    # Assert Parser called twice with the correct argument
    assert mock_parser.call_count == 2
    mock_parser.assert_any_call("SELECT col1 FROM nonexistent_table")


@patch("src.tools.validator_tool.Parser")
def test_check_schema_compatibility_invalid_column(mock_parser: MagicMock) -> None:
    """Test schema compatibility with invalid column."""
    mock_instance = MagicMock()
    mock_instance.tables = ["table1"]
    mock_instance.columns = ["nonexistent_column"]

    # Return same mock instance for both calls
    mock_parser.side_effect = [mock_instance, mock_instance]

    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    is_compatible, error = tool.check_schema_compatibility("SELECT nonexistent_column FROM table1")

    assert is_compatible is False
    assert "nonexistent_column" in error

    # Verify Parser was called twice with correct argument
    assert mock_parser.call_count == 2
    mock_parser.assert_any_call("SELECT nonexistent_column FROM table1")


def test_validate_sql_all_valid() -> None:
    """Test validating SQL when all checks pass."""
    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    tool.check_syntax = MagicMock(return_value=(True, None))
    tool.check_dangerous_patterns = MagicMock(return_value=(True, None))
    tool.check_schema_compatibility = MagicMock(return_value=(True, None))

    result = tool.validate_sql("SELECT col1 FROM table1")

    assert isinstance(result, ValidationResult)
    assert result.is_valid is True
    assert len(result.errors) == 0
    tool.check_syntax.assert_called_once()
    tool.check_dangerous_patterns.assert_called_once()
    tool.check_schema_compatibility.assert_called_once()


def test_validate_sql_with_errors() -> None:
    """Test validating SQL when errors are found."""
    tool = ValidatorTool(schema_dict={"table1": [{"column_name": "col1", "data_type": "INTEGER"}]})

    tool.check_syntax = MagicMock(return_value=(False, "Syntax error"))
    tool.check_dangerous_patterns = MagicMock(return_value=(True, None))
    tool.check_schema_compatibility = MagicMock(return_value=(False, "Schema error"))

    result = tool.validate_sql("SELEC col1 FRUM table1")

    assert isinstance(result, ValidationResult)
    assert result.is_valid is False
    assert len(result.errors) == 2
    assert "Syntax error" in result.errors
    assert "Schema error" in result.errors
    tool.check_syntax.assert_called_once()
    tool.check_dangerous_patterns.assert_called_once()
    tool.check_schema_compatibility.assert_called_once()
