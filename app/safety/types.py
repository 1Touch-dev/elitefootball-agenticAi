from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


class ActionKind(str, Enum):
    API_REQUEST = "api_request"
    AGENT_TASK = "agent_task"
    REPO_OPERATION = "repo_operation"
    SHELL_COMMAND = "shell_command"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONSUMED = "consumed"


@dataclass(frozen=True)
class SafetyCheckRequest:
    action_kind: ActionKind
    action_name: str
    command: str | None = None
    target_path: str | None = None
    requested_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SafetyEvaluation:
    decision: PolicyDecision
    reason_code: str
    message: str
    matched_rules: list[str] = field(default_factory=list)
    action_fingerprint: str | None = None
    approval_id: str | None = None
    expires_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["decision"] = self.decision.value
        return payload


@dataclass
class ApprovalRecord:
    approval_id: str
    status: ApprovalStatus
    request: SafetyCheckRequest
    action_fingerprint: str
    reason_code: str
    message: str
    matched_rules: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    resolved_at: datetime | None = None
    approver: str | None = None
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["request"] = self.request.to_dict()
        return payload
