import unittest

from app.safety.policies import evaluate_request
from app.safety.types import ActionKind, PolicyDecision, SafetyCheckRequest


class TestSafetyPolicies(unittest.TestCase):
    def test_denies_repo_delete_operation(self):
        evaluation = evaluate_request(
            SafetyCheckRequest(action_kind=ActionKind.REPO_OPERATION, action_name="delete_repo", target_path="/tmp/zero-human-sandbox"),
            repo_root="/tmp/zero-human-sandbox",
        )
        self.assertEqual(evaluation.decision, PolicyDecision.DENY)
        self.assertEqual(evaluation.reason_code, "repo_deletion_blocked")

    def test_denies_destructive_shell_command(self):
        evaluation = evaluate_request(
            SafetyCheckRequest(action_kind=ActionKind.SHELL_COMMAND, action_name="shell", command="rm -rf /tmp/zero-human-sandbox"),
            repo_root="/tmp/zero-human-sandbox",
        )
        self.assertEqual(evaluation.decision, PolicyDecision.DENY)
        self.assertIn("repo_root_targeted_delete", evaluation.matched_rules)

    def test_requires_approval_for_git_reset_hard(self):
        evaluation = evaluate_request(
            SafetyCheckRequest(action_kind=ActionKind.SHELL_COMMAND, action_name="shell", command="git reset --hard HEAD~1"),
            repo_root="/tmp/zero-human-sandbox",
        )
        self.assertEqual(evaluation.decision, PolicyDecision.REQUIRE_APPROVAL)
        self.assertIn("history_or_workspace_rewrite", evaluation.matched_rules)

    def test_allows_read_only_shell_command(self):
        evaluation = evaluate_request(
            SafetyCheckRequest(action_kind=ActionKind.SHELL_COMMAND, action_name="shell", command="git status"),
            repo_root="/tmp/zero-human-sandbox",
        )
        self.assertEqual(evaluation.decision, PolicyDecision.ALLOW)
        self.assertEqual(evaluation.reason_code, "read_only_command")


if __name__ == "__main__":
    unittest.main()
