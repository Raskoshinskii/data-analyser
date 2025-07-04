import pytest
from unittest.mock import patch, MagicMock

from src.tools.sql_tool import SQLTool
from src.models.schemas import SQLQuery


@patch('src.tools.sql_tool.ChatOpenAI')
def test_sql_tool_initialization(mock_chat_openai):
    """Test the initialization of the SQLTool."""
    # Setup
    mock_llm = MagicMock()
    
    # Create the tool
    tool = SQLTool(llm=mock_llm)
    
    # Assertions
    assert tool.llm == mock_llm


@patch('src.tools.sql_tool.ChatOpenAI')
def test_format_schema(mock_chat_openai):
    """Test formatting the schema."""
    # Setup
    mock_llm = MagicMock()
    
    schema_dict = {
        "table1": [
            {"column_name": "col1", "data_type": "INTEGER"},
            {"column_name": "col2", "data_type": "TEXT"}
        ]
    }
    
    # Create the tool
    tool = SQLTool(llm=mock_llm)
    
    # Format schema
    formatted_schema = tool.format_schema(schema_dict)
    
    # Assertions
    assert "table1" in formatted_schema
    assert "col1 (INTEGER)" in formatted_schema
    assert "col2 (TEXT)" in formatted_schema


@patch('src.tools.sql_tool.ChatOpenAI')
def test_generate_query(mock_chat_openai):
    """Test generating a SQL query."""
    # Setup
    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = """
    ```sql
    SELECT * FROM table1
    ```
    
    This query selects all columns from table1.
    
    Tables used: table1
    """
    
    schema_dict = {
        "table1": [
            {"column_name": "col1", "data_type": "INTEGER"},
            {"column_name": "col2", "data_type": "TEXT"}
        ]
    }
    
    # Create the tool
    tool = SQLTool(llm=mock_llm)
    
    # Generate query
    query = tool.generate_query(task_description="Get all data from table1", schema_dict=schema_dict)
    
    # Assertions
    assert isinstance(query, SQLQuery)
    assert "SELECT * FROM table1" in query.query
    assert "table1" in query.tables_used
    mock_llm.invoke.assert_called_once()