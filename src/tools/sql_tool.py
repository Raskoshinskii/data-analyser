import logging
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel
from src.models.schemas import SQLQuery

logger = logging.getLogger(__name__)

SQL_GENERATION_TEMPLATE = """
You are an expert SQL writer who helps generate safe and efficient SQL queries.

DATABASE SCHEMA:
{schema}

USER REQUEST: 
{task_description}

Write a SQL query that fulfills the user's request. The query should be:
1. Safe and well-formed
2. Efficient
3. Only use tables and columns that exist in the schema
4. Include appropriate JOINs, WHERE clauses, and aggregations as needed

Return ONLY the executable SQL query without any explanations, comments, or markdown formatting.
"""


class SQLTool:
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["schema", "task_description"],
            template=SQL_GENERATION_TEMPLATE
        )
        
    def format_schema(self, schema_dict):
        """Format the schema dictionary into a readable string for the prompt."""
        schema_text = ""
        for table, columns in schema_dict.items():
            schema_text += f"Table: {table}\n"
            schema_text += "Columns:\n"
            for col in columns:
                schema_text += f"  - {col['column_name']} ({col['data_type']})\n"
            schema_text += "\n"
        return schema_text
    
    def generate_query(self, task_description: str, schema_dict) -> SQLQuery:
        """Generate SQL query based on task description and schema."""
        schema_text = self.format_schema(schema_dict)
        
        prompt_value = self.prompt.format(
            schema=schema_text,
            task_description=task_description
        )
        
        logger.info(f"Generating SQL query for task: {task_description}")
        
        # Get the SQL query from the LLM
        try:
            response = self.llm.invoke(prompt_value)
            # Handle both string and AIMessage responses
            sql_text = response.content if hasattr(response, 'content') else response.strip()
            
            # Create enhanced prompt to get metadata about the query
            metadata_prompt = f"""
            For this SQL query:
            ```
            {sql_text}
            ```
            
            1. Provide a brief description of what this query does.
            2. List all tables used in this query.
            
            Format your response as:
            Description: <brief description>
            Tables: table1, table2, ...
            """
            
            metadata_response = self.llm.invoke(metadata_prompt)
            metadata_text = metadata_response.content if hasattr(metadata_response, 'content') else metadata_response
            
            description = ""
            tables = []
            
            for line in metadata_text.split("\n"):
                if line.startswith("Description:"):
                    description = line.replace("Description:", "").strip()
                elif line.startswith("Tables:"):
                    tables_text = line.replace("Tables:", "").strip()
                    tables = [t.strip() for t in tables_text.split(",")]
            
            logger.info(f"Successfully generated SQL query")
            
            return SQLQuery(
                query=sql_text,
                description=description,
                tables_used=tables
            )
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            raise
