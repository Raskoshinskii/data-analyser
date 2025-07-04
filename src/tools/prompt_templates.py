DANGEROUS_PATTERNS = [
    r'\bDROP\b', 
    r'\bDELETE\b', 
    r'\bTRUNCATE\b', 
    r'\bALTER\b', 
    r'\bUPDATE\b',
    r'\bGRANT\b',
    r'\bREVOKE\b',
    r'\bEXEC\b',
    r'\bINSERT\b'
]

INSIGHT_TEMPLATE = """
You are a data analyst providing insights on data analysis results.

ORIGINAL TASK DESCRIPTION: {task_description}

DATA ANALYSIS RESULTS:
{result_summary}

Based on the above data, provide:
1. A concise summary (2-3 sentences) highlighting the key findings
2. 1-3 specific key points or observations from the data
3. 1-3 actionable recommendations based on these insights (if applicable)

Format your response as follows:
Summary: <brief summary>

Key Points:
- <point 1>
- <point 2>
- ...

Recommendations:
- <point 1>
- <point 2>
- ...
"""

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