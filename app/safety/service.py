from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.config import settings
from app.safety.policies import action_fingerprint, evaluate_request
from app.safety.store import approval_store
from app.safety.types import ApprovalRecord, ApprovalStatus, PolicyDecision, SafetyCheckRequest, SafetyEvaluation


class SafetyDeniedError(PermissionError):
    def __init__(self, evaluation: SafetyEvaluation):
        super().__init__(evaluation.message)
        self.evaluation = evaluation


class ApprovalNotFoundError(KeyError):
    pass


def evaluate_action(request: SafetyCheckRequest, auto_create_approval: bool = True) -> SafetyEvaluation:
    evaluation = evaluate_request(request, repo_root=settings.repo_root)
    if evaluation.decision == PolicyDecision.REQUIRE_APPROVAL and auto_create_approval:
        record = create_approval_request(request, evaluation)
        return SafetyEvaluation(
            decision=evaluation.decision,
            reason_code=evaluation.reason_code,
            message=evaluation.message,
            matched_rules=list(evaluation.matched_rules),
            action_fingerprint=evaluation.action_fingerprint,
            approval_id=record.approval_id,
            expires_at=record.expires_at,
        )
    return evaluation


def assert_allowed(request: SafetyCheckRequest) -> SafetyEvaluation:
    evaluation = evaluate_action(request, auto_create_approval=False)
    if evaluation.decision == PolicyDecision.DENY:
        raise SafetyDeniedError(evaluation)
    return evaluation


def create_approval_request(request: SafetyCheckRequest, evaluation: SafetyEvaluation | None = None) -> ApprovalRecord:
    evaluation = evaluation or evaluate_request(request, repo_root=settings.repo_root)
    if evaluation.decision != PolicyDecision.REQUIRE_APPROVAL:
        raise ValueError("Approval requests can only be created for actions requiring approval.")

    now = datetime.now(UTC)
    record = ApprovalRecord(
        approval_id=str(uuid4()),
        status=ApprovalStatus.PENDING,
        request=request,
        action_fingerprint=evaluation.action_fingerprint or action_fingerprint(request),
        reason_code=evaluation.reason_code,
        message=evaluation.message,
        matched_rules=list(evaluation.matched_rules),
        created_at=now,
        expires_at=now + timedelta(seconds=settings.safety_approval_ttl_seconds),
    )
    return approval_store.save(record)


def get_approval(approval_id: str) -> ApprovalRecord:
    record = approval_store.get(approval_id)
    if record is None:
        raise ApprovalNotFoundError(f"Approval not found: {approval_id}")
    return record


def approve_request(approval_id: str, approver: str | None = None, note: str | None = None) -> ApprovalRecord:
    record = get_approval(approval_id)
    record.status = ApprovalStatus.EXPIRED if record.expires_at and record.expires_at < datetime.now(UTC) else ApprovalStatus.APPROVED
    record.resolved_at = datetime.now(UTC)
    record.approver = approver
    record.note = note
    return approval_store.save(record)


def reject_request(approval_id: str, approver: str | None = None, note: str | None = None) -> ApprovalRecord:
    record = get_approval(approval_id)
    record.status = ApprovalStatus.REJECTED
    record.resolved_at = datetime.now(UTC)
    record.approver = approver
    record.note = note
    return approval_store.save(record)


def resolve_approval(approval_id: str, request: SafetyCheckRequest, consume: bool = True) -> ApprovalRecord:
    record = get_approval(approval_id)
    if record.status != ApprovalStatus.APPROVED:
        raise PermissionError(f"Approval {approval_id} is not approved.")
    if record.expires_at and record.expires_at < datetime.now(UTC):
        record.status = ApprovalStatus.EXPIRED
        approval_store.save(record)
        raise PermissionError(f"Approval {approval_id} has expired.")
    if record.action_fingerprint != action_fingerprint(request):
        raise PermissionError("Approval does not match the requested action.")
    if consume:
        record.status = ApprovalStatus.CONSUMED
        record.resolved_at = datetime.now(UTC)
        approval_store.save(record)
    return record
