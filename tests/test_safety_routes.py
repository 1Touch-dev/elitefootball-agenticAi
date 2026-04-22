import importlib.util
import unittest
from unittest.mock import patch

FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None

if FASTAPI_AVAILABLE:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.safety.store import approval_store


@unittest.skipUnless(FASTAPI_AVAILABLE, "fastapi is not installed in this environment")
class TestSafetyRoutes(unittest.TestCase):
    def setUp(self):
        approval_store.clear()
        self.client = TestClient(app)

    def test_denied_command_returns_403(self):
        response = self.client.post(
            "/safety/evaluate",
            json={
                "action_kind": "shell_command",
                "action_name": "shell",
                "command": "rm -rf /tmp/zero-human-sandbox",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"]["status"], "denied")

    def test_approval_flow_round_trip(self):
        evaluate = self.client.post(
            "/safety/evaluate",
            json={
                "action_kind": "shell_command",
                "action_name": "shell",
                "command": "git reset --hard HEAD~1",
            },
        )
        self.assertEqual(evaluate.status_code, 200)
        payload = evaluate.json()
        self.assertEqual(payload["status"], "approval_required")

        approval_id = payload["approval_id"]
        self.assertIsNotNone(approval_id)

        approve = self.client.post(f"/approvals/{approval_id}/approve", json={"approver": "pedant"})
        self.assertEqual(approve.status_code, 200)
        self.assertEqual(approve.json()["status"], "approved")

        fetch = self.client.get(f"/approvals/{approval_id}")
        self.assertEqual(fetch.status_code, 200)
        self.assertEqual(fetch.json()["approval_id"], approval_id)


if __name__ == "__main__":
    unittest.main()
