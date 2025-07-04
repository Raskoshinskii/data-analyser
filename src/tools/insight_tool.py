import logging
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from src.models.schemas import QueryResult
from src.tools.prompt_templates import INSIGHT_TEMPLATE
from typing import Optional

logger = logging.getLogger(__name__)


class InsightTool:
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["task_description", "result_summary"],
            template=INSIGHT_TEMPLATE
        )
    
    def format_result_summary(self, query_result: QueryResult) -> str:
        """Format query results into a readable summary for the LLM."""
        summary = f"Total rows: {query_result.row_count}\n"
        summary += f"Columns: {', '.join(query_result.column_names)}\n\n"
        
        # Include sample data (up to 10 rows)
        data_sample = query_result.data[:10]
        if data_sample:
            summary += "Data sample:\n"
            for row in data_sample:
                summary += str(row) + "\n"
                
        return summary
    
    def generate_insights(self, task_description: str, query_result: QueryResult) -> Optional[str]:
        """Generate business insights from query results."""
        result_summary = self.format_result_summary(query_result)
        
        prompt_value = self.prompt.format(
            task_description=task_description,
            result_summary=result_summary
        )
        
        logger.info(f"Generating insights for task: {task_description}")
        
        try:
            response = self.llm.invoke(prompt_value)

            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                logger.error(f"Empty response from LLM")

        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
