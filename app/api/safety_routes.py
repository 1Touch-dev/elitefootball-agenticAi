from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.safety.schemas import ApprovalDecisionRequest, ApprovalRecordResponse, SafetyEvaluationRequest, SafetyEvaluationResponse
from app.safety.service import ApprovalNotFoundError, approve_request, evaluate_action, get_approval, reject_request
from app.safety.types import PolicyDecision, SafetyCheckRequest

router = APIRouter()


def _to_response_status(decision: PolicyDecision) -> str:
    if decision == PolicyDecision.DENY:
        return "denied"
    if decision == PolicyDecision.REQUIRE_APPROVAL:
        return "approval_required"
    return "allowed"


def _record_to_response(record) -> ApprovalRecordResponse:
    return ApprovalRecordResponse(
        approval_id=record.approval_id,
        status=record.status.value,
        reason_code=record.reason_code,
        message=record.message,
        matched_rules=list(record.matched_rules),
        action_fingerprint=record.action_fingerprint,
        created_at=record.created_at,
        expires_at=record.expires_at,
        resolved_at=record.resolved_at,
        approver=record.approver,
        note=record.note,
        request=record.request.to_dict(),
    )


@router.post("/safety/evaluate", response_model=SafetyEvaluationResponse)
def evaluate_safety(request: SafetyEvaluationRequest):
    evaluation = evaluate_action(
        SafetyCheckRequest(
            action_kind=request.action_kind,
            action_name=request.action_name,
            command=request.command,
            target_path=request.target_path,
            requested_by=request.requested_by,
            metadata=dict(request.metadata),
        )
    )
    response = SafetyEvaluationResponse(
        status=_to_response_status(evaluation.decision),
        decision=evaluation.decision.value,
        reason_code=evaluation.reason_code,
        message=evaluation.message,
        matched_rules=list(evaluation.matched_rules),
        action_fingerprint=evaluation.action_fingerprint,
        approval_id=evaluation.approval_id,
        expires_at=evaluation.expires_at,
    )
    if evaluation.decision == PolicyDecision.DENY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=response.model_dump())
    if evaluation.decision == PolicyDecision.REQUIRE_APPROVAL:
        return response
    return response


@router.get("/approvals/{approval_id}", response_model=ApprovalRecordResponse)
def read_approval(approval_id: str) -> ApprovalRecordResponse:
    try:
        return _record_to_response(get_approval(approval_id))
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalRecordResponse)
def approve_approval(approval_id: str, request: ApprovalDecisionRequest) -> ApprovalRecordResponse:
    try:
        return _record_to_response(approve_request(approval_id, approver=request.approver, note=request.note))
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalRecordResponse)
def reject_approval(approval_id: str, request: ApprovalDecisionRequest) -> ApprovalRecordResponse:
    try:
        return _record_to_response(reject_request(approval_id, approver=request.approver, note=request.note))
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
