from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.safety.types import ActionKind


class SafetyEvaluationRequest(BaseModel):
    action_kind: ActionKind
    action_name: str
    command: str | None = None
    target_path: str | None = None
    requested_by: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SafetyEvaluationResponse(BaseModel):
    status: str
    decision: str
    reason_code: str
    message: str
    matched_rules: list[str] = Field(default_factory=list)
    action_fingerprint: str | None = None
    approval_id: str | None = None
    expires_at: datetime | None = None


class ApprovalDecisionRequest(BaseModel):
    approver: str | None = None
    note: str | None = None


class ApprovalRecordResponse(BaseModel):
    approval_id: str
    status: str
    reason_code: str
    message: str
    matched_rules: list[str] = Field(default_factory=list)
    action_fingerprint: str
    created_at: datetime
    expires_at: datetime | None = None
    resolved_at: datetime | None = None
    approver: str | None = None
    note: str | None = None
    request: dict[str, Any]
