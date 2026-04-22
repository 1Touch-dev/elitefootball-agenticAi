from __future__ import annotations

from datetime import UTC, datetime
from typing import Dict

from app.safety.types import ApprovalRecord, ApprovalStatus


class InMemoryApprovalStore:
    def __init__(self) -> None:
        self._records: Dict[str, ApprovalRecord] = {}

    def save(self, record: ApprovalRecord) -> ApprovalRecord:
        self._records[record.approval_id] = record
        return record

    def get(self, approval_id: str) -> ApprovalRecord | None:
        record = self._records.get(approval_id)
        if record and record.expires_at and record.expires_at < datetime.now(UTC) and record.status == ApprovalStatus.PENDING:
            record.status = ApprovalStatus.EXPIRED
        return record

    def clear(self) -> None:
        self._records.clear()


approval_store = InMemoryApprovalStore()
