from unittest.mock import MagicMock, patch

from src.clients.db_client import DatabaseClient
from src.models.schemas import QueryResult


@patch("src.clients.db_client.create_engine")
@patch("src.clients.db_client.inspect")
def test_db_client_initialization(
    mock_inspect: MagicMock, mock_create_engine: MagicMock
) -> None:
    """Test the initialization of the DatabaseClient."""
    # Setup
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    mock_inspector = MagicMock()
    mock_inspect.return_value = mock_inspector

    # Create the client
    client = DatabaseClient("sqlite:///test.db")

    # Assertions
    mock_create_engine.assert_called_once_with("sqlite:///test.db")
    assert client.engine == mock_engine
    assert client.inspector == mock_inspector


@patch("src.clients.db_client.create_engine")
@patch("src.clients.db_client.inspect")
def test_get_tables(mock_inspect: MagicMock, mock_create_engine: MagicMock) -> None:
    """Test getting tables from the database."""
    # Setup
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = ["table1", "table2"]
    mock_inspect.return_value = mock_inspector

    # Create the client
    client = DatabaseClient("sqlite:///test.db")

    # Get tables
    tables = client.get_tables()

    # Assertions
    assert tables == ["table1", "table2"]
    mock_inspector.get_table_names.assert_called_once()


@patch("src.clients.db_client.create_engine")
@patch("src.clients.db_client.inspect")
def test_get_schema(mock_inspect: MagicMock, mock_create_engine: MagicMock) -> None:
    """Test getting schema from the database."""
    # Setup
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = ["table1"]
    mock_inspector.get_columns.return_value = [
        {"name": "col1", "type": "INTEGER"},
        {"name": "col2", "type": "TEXT"},
    ]
    mock_inspect.return_value = mock_inspector

    # Create the client
    client = DatabaseClient("sqlite:///test.db")

    # Get schema
    schema = client.get_schema()

    # Assertions
    assert "table1" in schema
    assert len(schema["table1"]) == 2
    assert schema["table1"][0]["column_name"] == "col1"
    assert schema["table1"][0]["data_type"] == "INTEGER"
    mock_inspector.get_table_names.assert_called_once()
    mock_inspector.get_columns.assert_called_once_with("table1")


@patch("src.clients.db_client.create_engine")
@patch("src.clients.db_client.inspect")
@patch("src.clients.db_client.text")
def test_execute_query(
    mock_text: MagicMock, mock_inspect: MagicMock, mock_create_engine: MagicMock
) -> None:
    """Test executing a query."""
    # Setup
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    mock_inspector = MagicMock()
    mock_inspect.return_value = mock_inspector

    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    mock_result = MagicMock()
    mock_result.keys.return_value = ["col1", "col2"]
    mock_result.fetchall.return_value = [{"col1": "val1", "col2": "val2"}]
    mock_connection.execute.return_value = mock_result

    # Create the client
    client = DatabaseClient("sqlite:///test.db")

    # Execute query
    result = client.execute_query("SELECT * FROM table1")

    # Assertions
    assert isinstance(result, QueryResult)
    assert result.data == [{"col1": "val1", "col2": "val2"}]
    assert result.column_names == ["col1", "col2"]
    assert result.row_count == 1
    mock_connection.execute.assert_called_once()
