import time
import logging
from typing import List, Dict
import pandas as pd
from sqlalchemy import create_engine, text
from src.models.schemas import QueryResult

logger = logging.getLogger(__name__)


class DatabaseClient:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.connection = None
        self.is_sqlite = connection_string.startswith('sqlite://') # detect if we're using SQLite
        
    def connect(self):
        if self.connection is None or self.connection.closed:
            self.connection = self.engine.connect()
        return self.connection
            
    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def get_database_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """Fetch database schema information."""
        if self.is_sqlite:
            query = """
            SELECT 
                m.name as table_name, 
                p.name as column_name,
                p.type as data_type
            FROM 
                sqlite_master m
            LEFT JOIN 
                pragma_table_info(m.name) p
            WHERE 
                m.type = 'table' AND
                m.name NOT LIKE 'sqlite_%'
            """
        else:
            # postgreSQL related
            query = """
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public'
            """
        
        with self.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            
        schema_dict = {}
        for row in rows:
            table_name = row[0]
            if table_name not in schema_dict:
                schema_dict[table_name] = []
                
            schema_dict[table_name].append({
                "column_name": row[1],
                "data_type": row[2]
            })
            
        return schema_dict
        
    def execute_query(self, sql_query: str) -> QueryResult:
        """Execute SQL query and return results."""
        start_time = time.time()
        try:
            with self.connect() as conn:
                # use pandas to execute the query and get results
                df = pd.read_sql(sql_query, conn)
                
            execution_time = (time.time() - start_time) * 1000  # convert to milliseconds
            
            # convert DataFrame to QueryResult
            result = QueryResult(
                data=df.to_dict(orient="records"),
                row_count=len(df),
                column_names=df.columns.tolist(),
                execution_time_ms=execution_time
            )
            
            logger.info(f"Query executed successfully. Returned {result.row_count} rows.")
            return result
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
