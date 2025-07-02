import logging
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel

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
3. Only use tables and columns that exist in the schema, use DATABASE SCHEMA
4. Include appropriate JOINs, WHERE clauses, and aggregations as needed

Return ONLY the executable SQL query without any explanations, comments, or markdown formatting.
"""


class SQLTool:
    def __init__(self, llm: BaseLanguageModel, db_schema: dict = None):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["schema", "task_description"],
            template=SQL_GENERATION_TEMPLATE
        )
        self.db_schema = self.db_schema
    
        
    def _format_schema(self, schema_dict: dict) -> str:
        """Format the schema dictionary into a readable string for the prompt."""
        schema_text = ""
        for table, columns in schema_dict.items():
            schema_text += f"Table: {table}\n"
            schema_text += "Columns:\n"
            for col in columns:
                schema_text += f"  - {col['column_name']} ({col['data_type']})\n"
            schema_text += "\n"
        return schema_text


    def generate_query(self, task_description: str) -> str:
        """Generate SQL query based on task description and schema."""
        schema_text = self._format_schema(self.db_schema)
        
        prompt_value = self.prompt.format(
            schema=schema_text,
            task_description=task_description
        )
        
        logger.info(f"Generating SQL query for task: {task_description}")

        try:
            response = self.llm.invoke(prompt_value)

            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                logger.error(f"Empty response from LLM")

        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")

