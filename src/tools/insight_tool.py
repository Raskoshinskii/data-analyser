import logging
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from src.models.schemas import QueryResult, BusinessInsight

logger = logging.getLogger(__name__)

INSIGHT_TEMPLATE = """
You are a business analyst providing insights on data analysis results.

ORIGINAL TASK DESCRIPTION: {task_description}

DATA ANALYSIS RESULTS:
{result_summary}

Based on the above data, provide:
1. A concise summary (2-3 sentences) highlighting the key findings
2. 3-5 specific key points or observations from the data
3. 1-3 actionable recommendations based on these insights (if applicable)

Format your response as follows:
Summary: <brief summary>

Key Points:
- <point 1>
- <point 2>
- ...

Recommendations:
- <recommendation 1>
- <recommendation 2>
- ...
"""


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
    
    def generate_insights(self, task_description: str, query_result: QueryResult) -> BusinessInsight:
        """Generate business insights from query results."""
        result_summary = self.format_result_summary(query_result)
        
        prompt_value = self.prompt.format(
            task_description=task_description,
            result_summary=result_summary
        )
        
        logger.info(f"Generating insights for task: {task_description}")
        
        try:
            response = self.llm.invoke(prompt_value)
            
            # Parse the response
            summary = ""
            key_points = []
            recommendations = []
            
            current_section = None
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("Summary:"):
                    current_section = "summary"
                    summary = line.replace("Summary:", "").strip()
                elif line.startswith("Key Points:"):
                    current_section = "key_points"
                elif line.startswith("Recommendations:"):
                    current_section = "recommendations"
                elif line.startswith("-") and current_section == "key_points":
                    key_points.append(line[1:].strip())
                elif line.startswith("-") and current_section == "recommendations":
                    recommendations.append(line[1:].strip())
            
            # Ensure we have at least some key points
            if not key_points:
                key_points = ["No specific patterns identified in the data."]
            
            logger.info(f"Successfully generated insights with {len(key_points)} key points")
            
            return BusinessInsight(
                summary=summary,
                key_points=key_points,
                recommendations=recommendations if recommendations else None
            )
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            default_insight = BusinessInsight(
                summary="Unable to generate detailed insights due to an error.",
                key_points=["The data was processed but insights generation failed."],
                recommendations=["Please review the raw data manually."]
            )
            return default_insight
