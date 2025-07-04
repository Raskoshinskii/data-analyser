from unittest.mock import MagicMock, patch

from src.models.schemas import ValidationResult
from src.tools.validator_tool import ValidatorTool


@patch("src.tools.validator_tool.ChatOpenAI")
def test_validator_tool_initialization(mock_chat_openai: MagicMock) -> None:
    """Test the initialization of the ValidatorTool."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Assertions
    assert tool.llm == mock_llm
    assert tool.schema_dict == schema_dict


@patch("src.tools.validator_tool.ChatOpenAI")
@patch("src.tools.validator_tool.sqlparse")
def test_check_syntax_valid(
    mock_sqlparse: MagicMock, mock_chat_openai: MagicMock
) -> None:
    """Test checking syntax with valid SQL."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    mock_sqlparse.format.return_value = "SELECT * FROM table1"
    mock_sqlparse.parse.return_value = [MagicMock()]

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Check syntax
    is_valid, error = tool.check_syntax("SELECT * FROM table1")

    # Assertions
    assert is_valid is True
    assert error is None
    mock_sqlparse.format.assert_called_once()
    mock_sqlparse.parse.assert_called_once()


@patch("src.tools.validator_tool.ChatOpenAI")
@patch("src.tools.validator_tool.sqlparse")
def test_check_syntax_invalid(
    mock_sqlparse: MagicMock, mock_chat_openai: MagicMock
) -> None:
    """Test checking syntax with invalid SQL."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    mock_sqlparse.format.return_value = "SELEC * FRUM table1"  # Intentional errors
    mock_sqlparse.parse.return_value = []  # Empty list indicates parse failure

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Check syntax
    is_valid, error = tool.check_syntax("SELEC * FRUM table1")

    # Assertions
    assert is_valid is False
    assert error == "Invalid Syntax"
    mock_sqlparse.format.assert_called_once()
    mock_sqlparse.parse.assert_called_once()


@patch("src.tools.validator_tool.ChatOpenAI")
def test_check_dangerous_patterns_safe(mock_chat_openai: MagicMock) -> None:
    """Test checking for dangerous patterns with safe SQL."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Check dangerous patterns
    is_safe, error = tool.check_dangerous_patterns("SELECT * FROM table1")

    # Assertions
    assert is_safe is True
    assert error is None


@patch("src.tools.validator_tool.ChatOpenAI")
def test_check_dangerous_patterns_unsafe(mock_chat_openai: MagicMock) -> None:
    """Test checking for dangerous patterns with unsafe SQL."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Check dangerous patterns
    is_safe, error = tool.check_dangerous_patterns("DROP TABLE table1")

    # Assertions
    assert is_safe is False
    assert "DROP" in error


@patch("src.tools.validator_tool.ChatOpenAI")
def test_check_schema_compatibility_valid(mock_chat_openai: MagicMock) -> None:
    """Test checking schema compatibility with valid SQL."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Check schema compatibility
    is_compatible, error = tool.check_schema_compatibility("SELECT col1 FROM table1")

    # Assertions
    assert is_compatible is True
    assert error is None


@patch("src.tools.validator_tool.ChatOpenAI")
@patch("src.tools.validator_tool.extract_tables")
def test_check_schema_compatibility_invalid(
    mock_extract_tables: MagicMock, mock_chat_openai: MagicMock
) -> None:
    """Test checking schema compatibility with invalid SQL."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    mock_extract_tables.return_value = ["nonexistent_table"]

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Check schema compatibility
    is_compatible, error = tool.check_schema_compatibility(
        "SELECT * FROM nonexistent_table"
    )

    # Assertions
    assert is_compatible is False
    assert "nonexistent_table" in error
    mock_extract_tables.assert_called_once()


@patch("src.tools.validator_tool.ChatOpenAI")
def test_validate_sql_all_valid(mock_chat_openai: MagicMock) -> None:
    """Test validating SQL with all checks passing."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Patch the individual check methods
    tool.check_syntax = MagicMock(return_value=(True, None))
    tool.check_dangerous_patterns = MagicMock(return_value=(True, None))
    tool.check_schema_compatibility = MagicMock(return_value=(True, None))

    # Validate SQL
    result = tool.validate_sql("SELECT col1 FROM table1", "Get col1 from table1")

    # Assertions
    assert isinstance(result, ValidationResult)
    assert result.is_valid is True
    assert len(result.errors) == 0
    tool.check_syntax.assert_called_once()
    tool.check_dangerous_patterns.assert_called_once()
    tool.check_schema_compatibility.assert_called_once()


@patch("src.tools.validator_tool.ChatOpenAI")
def test_validate_sql_with_errors(mock_chat_openai: MagicMock) -> None:
    """Test validating SQL with errors."""
    # Setup
    mock_llm = MagicMock()
    schema_dict = {"table1": [{"column_name": "col1", "data_type": "INTEGER"}]}

    # Create the tool
    tool = ValidatorTool(llm=mock_llm, schema_dict=schema_dict)

    # Patch the individual check methods
    tool.check_syntax = MagicMock(return_value=(False, "Syntax error"))
    tool.check_dangerous_patterns = MagicMock(return_value=(True, None))
    tool.check_schema_compatibility = MagicMock(return_value=(False, "Schema error"))

    # Validate SQL
    result = tool.validate_sql("SELEC col1 FRUM table1", "Get col1 from table1")

    # Assertions
    assert isinstance(result, ValidationResult)
    assert result.is_valid is False
    assert len(result.errors) == 2
    assert "Syntax error" in result.errors
    assert "Schema error" in result.errors
    tool.check_syntax.assert_called_once()
    tool.check_dangerous_patterns.assert_called_once()
    tool.check_schema_compatibility.assert_called_once()
