import logging
import re
from typing import List, Optional, Set, Tuple

import sqlvalidator
from langchain_core.language_models import BaseLanguageModel
from sql_metadata import Parser

from src.models.schemas import QueryResult, ValidationResult

logger = logging.getLogger(__name__)

DANGEROUS_PATTERNS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bTRUNCATE\b",
    r"\bALTER\b",
    r"\bUPDATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bINSERT\b",
]

VALIDATION_PROMPT = """
You are an expert SQL validator. Please analyze this SQL query to ensure it meets the requirements:

TASK DESCRIPTION: {task_description}

SQL QUERY:
```sql
{sql_query}
```

Validate if the SQL query:
1. Correctly addresses the task described above
2. Uses appropriate tables and joins
3. Contains logical errors or inconsistencies
4. Could be optimized or improved

If the query has issues, explain what's wrong and suggest a fix.
If the query is valid, simply state "VALID: The query correctly addresses the task."

Your analysis:
"""


class ValidatorTool:
    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        schema_dict: Optional[dict] = None,
    ):
        self.llm = llm
        self.schema_dict = schema_dict
        self.schema_columns = (
            self._get_columns_from_schema(schema_dict) if schema_dict else set()
        )
        self.schema_tables = set(self.schema_dict) if schema_dict else set()

    def _get_columns_from_schema(self, schema: dict) -> Set[str]:
        """
        Extract all columns from the schema dictionary.
        """
        schema_columns = set()
        for columns in schema.values():
            for column in columns:
                schema_columns.add(column["column_name"])
        return schema_columns

    def _get_columns(self, query: str) -> Set[Optional[str]]:
        """
        Extract columns from SQL query using sql_metadata.
        """
        columns = Parser(query).columns
        return set([column.split(".")[-1] for column in columns])

    def _get_tables(self, query: str) -> Set[Optional[str]]:
        """
        Extract tables from SQL query.
        """
        parser = Parser(query)
        return set(parser.tables)

    def check_syntax(self, query: str) -> Tuple[bool, Optional[str]]:
        """Check SQL syntax."""
        parsed = sqlvalidator.parse(query)
        if not parsed.is_valid():
            return False, "Invalid Syntax"
        return True, None

    def check_dangerous_patterns(self, query: str) -> Tuple[bool, Optional[str]]:
        """Check for dangerous SQL operations."""
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                operation = re.search(pattern, query, re.IGNORECASE).group(0)
                return False, f"Dangerous operation: {operation}"
        return True, None

    def check_schema_compatibility(self, query: str) -> Tuple[bool, Optional[str]]:
        """Check if query uses tables and columns that exist in the schema."""

        if not self.schema_dict:
            logger.warning("No schema provided for validation")
            return False, []

        try:
            tables = self._get_tables(query)
            columns = self._get_columns(query)
        except Exception as e:
            return False, "Invalid Syntax"

        for table in tables:
            if table not in self.schema_tables:
                return False, f"Table '{table}' doesn't exist in the schema"

        for column in columns:
            if column not in self.schema_columns:
                return False, f"Column '{column}' doesn't exist in the schema"

        return True, None

    def validate_sql(self, sql_query: str) -> ValidationResult:
        """Validate SQL query using multiple checks."""
        errors = []
        warnings = []  # TODO: align in the future if it's needed
        suggestion = None

        # syntax validation
        syntax_valid, syntax_error = self.check_syntax(sql_query)
        if not syntax_valid:
            errors.append(syntax_error)

        # dangerous patterns validation
        safe, safety_error = self.check_dangerous_patterns(sql_query)
        if not safe:
            errors.append(safety_error)

        # schema compatibility validation
        schema_valid, schema_error = self.check_schema_compatibility(sql_query)
        if not schema_valid:
            errors.append(schema_error)

        # final validation
        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid, errors=errors, warnings=warnings, suggestion=suggestion
        )

        # TODO: align in the future if it's needed
        # # If basic checks pass, perform semantic validation with LLM
        # if syntax_valid and schema_valid:
        #     semantic_valid, semantic_issues, sem_suggestion = self.validate_query_semantic(
        #         sql_query, task_description
        #     )
        #     if not semantic_valid:
        #         all_warnings.extend(semantic_issues)
        #         suggestion = sem_suggestion

        # is_valid = len(all_errors) == 0

    # def validate_query_semantic(self, sql_query: SQLQuery, task_description: str) -> Tuple[bool, List[str], Optional[str]]:
    #     """Use LLM to validate that query semantically matches the task."""
    #     if not self.llm:
    #         logger.warning("No LLM provided for semantic validation")
    #         return True, [], None

    #     prompt = VALIDATION_PROMPT.format(
    #         task_description=task_description,
    #         sql_query=sql_query.query
    #     )

    #     try:
    #         response = self.llm.invoke(prompt)

    #         # Check if the response indicates the query is valid
    #         if response.startswith("VALID:"):
    #             return True, [], None

    #         # Extract feedback and suggestion
    #         lines = response.split('\n')
    #         errors = [line for line in lines if line and not line.startswith("VALID:")]

    #         # Try to find a suggestion for fixing the query
    #         suggestion = None
    #         if "```sql" in response:
    #             # Extract the SQL suggestion between backticks
    #             sql_parts = response.split("```sql")
    #             if len(sql_parts) > 1:
    #                 suggestion_parts = sql_parts[1].split("```")
    #                 if suggestion_parts:
    #                     suggestion = suggestion_parts[0].strip()

    #         return False, errors, suggestion

    #     except Exception as e:
    #         logger.error(f"Error in semantic validation: {str(e)}")
    #         return False, [f"Semantic validation error: {str(e)}"], None

    # def validate_query_results(self, query_result: QueryResult, task_description: str) -> ValidationResult:
    #     """Validate that query results are reasonable for the task."""
    #     errors = []
    #     warnings = []

    #     # Check if query returned any data
    #     if query_result.row_count == 0:
    #         warnings.append("Query returned no results. This may be expected but verify the query conditions.")

    #     # Check for too many results (might indicate a missing WHERE clause)
    #     if query_result.row_count > 10000:
    #         warnings.append(f"Query returned {query_result.row_count} rows, which is unusually large. Consider adding filters.")

    #     # Use LLM to validate results if available
    #     if self.llm:
    #         try:
    #             # Sample data for the LLM (limit to first 10 rows)
    #             sample_data = query_result.data[:10]

    #             prompt = f"""
    #             TASK: {task_description}

    #             QUERY RESULTS:
    #             Number of rows: {query_result.row_count}
    #             Columns: {', '.join(query_result.column_names)}

    #             Sample data (first {len(sample_data)} rows):
    #             {sample_data}

    #             Do these results appear to answer the task correctly? Consider:
    #             1. Do the columns match what's needed for the task?
    #             2. Does the data look relevant to the task?
    #             3. Are there any anomalies or issues with the results?

    #             If the results seem problematic, explain why. Otherwise, state "VALID: The results appear to address the task correctly."
    #             """

    #             response = self.llm.invoke(prompt)

    #             if not response.startswith("VALID:"):
    #                 warnings.append(f"Possible issues with results: {response}")
    #         except Exception as e:
    #             logger.error(f"Error validating results with LLM: {str(e)}")

    #     is_valid = len(errors) == 0

    #     return ValidationResult(
    #         is_valid=is_valid,
    #         errors=errors,
    #         warnings=warnings,
    #         suggestion=None
    #     )
