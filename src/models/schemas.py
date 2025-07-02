from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    FAILED = "FAILED"


class JiraTicket(BaseModel):
    ticket_id: str
    summary: str
    description: str
    status: TicketStatus
    assignee: Optional[str] = None


# class SQLQuery(BaseModel):
#     query: str
#     description: str = Field(description="Human-readable explanation of what the query does")
#     tables_used: List[str] = Field(default_factory=list)

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


class AgentState(BaseModel):
    """State maintained throughout the agent's workflow"""
    ticket: JiraTicket
    task_description: Optional[str] = None
    # sql_query: Optional[SQLQuery] = None
    sql_query: Optional[str] = None
    validation_result: Optional[ValidationResult] = None
    query_result: Optional[QueryResult] = None
    business_insight: Optional[BusinessInsight] = None
    error_message: Optional[str] = None
    retry_count: int = 0
