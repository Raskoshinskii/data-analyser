from unittest.mock import MagicMock, patch
from src.clients.db_client import DatabaseClient
import pandas as pd

@patch("src.clients.db_client.create_engine")
def test_db_client_initialization(mock_create_engine: MagicMock) -> None:
    """
    Unit test for verifying the initialization behavior of the DatabaseClient.

    This test ensures that:
    - The `create_engine` function from SQLAlchemy is called exactly once with the correct connection string.
    - The resulting engine is correctly assigned to the `engine` attribute of the DatabaseClient instance.

    Args:
        mock_create_engine (MagicMock): A mock object that replaces `create_engine` during the test.
    """
    # change the behaviour of SQLAlchemy "create_engine" to mock
    mock_engine = MagicMock()

    # when "create_engine" is called, returns the mock engine!!!
    mock_create_engine.return_value = mock_engine

    # check that the DatabaseClient called only once with the correct connection string!
    client = DatabaseClient(connection_string="sqlite:///test.db")
    mock_create_engine.assert_called_once_with("sqlite:///test.db")

    assert client.engine == mock_engine


@patch("src.clients.db_client.create_engine")
@patch("src.clients.db_client.text")
def test_get_database_schema(mock_text: MagicMock, mock_create_engine: MagicMock) -> None:
    """Test schema extraction logic."""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_result = MagicMock()

    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    mock_conn.execute.return_value = mock_result

    mock_result.fetchall.return_value = [
        ("users", "id", "INTEGER"),
        ("users", "name", "TEXT"),
        ("orders", "order_id", "INTEGER"),
    ]
    

    client = DatabaseClient("sqlite:///test.db")
    schema = client.get_database_schema()

    expected = {
        "users": [
            {"column_name": "id", "data_type": "INTEGER"},
            {"column_name": "name", "data_type": "TEXT"},
        ],
        "orders": [
            {"column_name": "order_id", "data_type": "INTEGER"},
        ],
    }
    assert schema == expected


@patch("src.clients.db_client.pd.read_sql")
@patch("src.clients.db_client.create_engine")
def test_execute_query(mock_create_engine: MagicMock, mock_read_sql: MagicMock) -> None:
    """Test query execution and QueryResult formatting."""
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    df = pd.DataFrame([{"col1": "a", "col2": 123}])
    mock_read_sql.return_value = df

    client = DatabaseClient("sqlite:///test.db")
    result = client.execute_query("SELECT * FROM table")

    assert result.data == [{"col1": "a", "col2": 123}]
    assert result.row_count == 1
    assert result.column_names == ["col1", "col2"]
    assert isinstance(result.execution_time_ms, float)
    mock_read_sql.assert_called_once()
