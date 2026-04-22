import unittest

from app.safety.service import approve_request, evaluate_action, get_approval, reject_request, resolve_approval
from app.safety.store import approval_store
from app.safety.types import ActionKind, ApprovalStatus, PolicyDecision, SafetyCheckRequest


class TestSafetyService(unittest.TestCase):
    def setUp(self):
        approval_store.clear()

    def test_auto_creates_approval_for_risky_command(self):
        evaluation = evaluate_action(
            SafetyCheckRequest(action_kind=ActionKind.SHELL_COMMAND, action_name="shell", command="git reset --hard HEAD~1")
        )
        self.assertEqual(evaluation.decision, PolicyDecision.REQUIRE_APPROVAL)
        self.assertIsNotNone(evaluation.approval_id)
        record = get_approval(evaluation.approval_id)
        self.assertEqual(record.status, ApprovalStatus.PENDING)

    def test_approve_then_consume_matching_action(self):
        request = SafetyCheckRequest(action_kind=ActionKind.SHELL_COMMAND, action_name="shell", command="git reset --hard HEAD~1")
        evaluation = evaluate_action(request)
        record = approve_request(evaluation.approval_id, approver="pedant")
        self.assertEqual(record.status, ApprovalStatus.APPROVED)

        consumed = resolve_approval(evaluation.approval_id, request)
        self.assertEqual(consumed.status, ApprovalStatus.CONSUMED)
        self.assertEqual(get_approval(evaluation.approval_id).status, ApprovalStatus.CONSUMED)

    def test_reject_request(self):
        evaluation = evaluate_action(
            SafetyCheckRequest(action_kind=ActionKind.SHELL_COMMAND, action_name="shell", command="git checkout -- .")
        )
        record = reject_request(evaluation.approval_id, approver="pedant")
        self.assertEqual(record.status, ApprovalStatus.REJECTED)

    def test_rejects_mismatched_action_fingerprint(self):
        request = SafetyCheckRequest(action_kind=ActionKind.SHELL_COMMAND, action_name="shell", command="git reset --hard HEAD~1")
        evaluation = evaluate_action(request)
        approve_request(evaluation.approval_id, approver="pedant")

        with self.assertRaises(PermissionError):
            resolve_approval(
                evaluation.approval_id,
                SafetyCheckRequest(action_kind=ActionKind.SHELL_COMMAND, action_name="shell", command="git reset --hard HEAD~2"),
            )


if __name__ == "__main__":
    unittest.main()
