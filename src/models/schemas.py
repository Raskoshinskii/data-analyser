from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[Optional[str]]
    warnings: List[Optional[str]]
    suggestion: Optional[str]


class QueryResult(BaseModel):
    data: List[Dict[str, Any]]
    row_count: int
    column_names: List[str]
    execution_time_ms: float


class BusinessInsight(BaseModel):
    summary: str
    key_points: List[str] = Field(default_factory=list)
    recommendations: Optional[List[str]] = None


class JiraTicket(BaseModel):
    ticket_id: str
    summary: str
    description: str
    status: str
    assignee: Optional[str] = None


class AgentState(BaseModel):
    """State maintained throughout the agent's workflow"""

    ticket: JiraTicket
    current_task: Optional[str] = None
    sql_query: Optional[str] = None
    validation_result: Optional[ValidationResult] = None
    query_result: Optional[QueryResult] = None
    business_insight: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
