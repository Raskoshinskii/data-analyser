from unittest.mock import patch, MagicMock
from src.tools.sql_tool import SQLTool



def test_sql_tool_initialization():
    """Test the initialization of the SQLTool."""
    mock_llm = MagicMock()
    tool = SQLTool(llm=mock_llm)
    assert tool.llm == mock_llm


def test_format_schema():
    mock_llm = MagicMock()
    schema_dict = {
        "table1": [
            {"column_name": "col1", "data_type": "INTEGER"},
            {"column_name": "col2", "data_type": "TEXT"},
        ]
    }
    tool = SQLTool(llm=mock_llm)
    formatted_schema = tool._format_schema(schema_dict)
    assert "table1" in formatted_schema
    assert "col1 (INTEGER)" in formatted_schema
    assert "col2 (TEXT)" in formatted_schema


def test_generate_query():
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
            {"column_name": "col2", "data_type": "TEXT"},
        ]
    }
    tool = SQLTool(llm=mock_llm, db_schema=schema_dict)
    query = tool.generate_query(task_description="Get all data from table1")
    assert isinstance(query, str)
    assert "SELECT * FROM table1" in query
    assert "table1" in query
    mock_llm.invoke.assert_called_once()