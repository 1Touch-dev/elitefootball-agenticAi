import importlib.util
import unittest
from unittest.mock import MagicMock, patch

FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None

if FASTAPI_AVAILABLE:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.tasks.schemas import TaskSubmissionRequest


@unittest.skipUnless(FASTAPI_AVAILABLE, "fastapi is not installed in this environment")
class TestTaskRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.submission_request = TaskSubmissionRequest(
            task_kind="run_analysis",
            payload={"example_key": "example_value"},
            requested_by="test_suite",
        )

    @patch("app.tasks.service.celery_app")
    @patch("app.tasks.service.route_task")
    def test_create_task_success(self, mock_route_task, mock_celery_app):
        mock_route_task.return_value = ["analyst"]
        mock_celery_app.send_task.return_value = MagicMock(id="mock_task_id")

        response = self.client.post("/api/tasks", json=self.submission_request.dict())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["task_id"], "mock_task_id")

    @patch("app.tasks.service.celery_app", None)
    def test_create_task_queue_unavailable(self):
        response = self.client.post("/api/tasks", json=self.submission_request.dict())
        self.assertEqual(response.status_code, 503)
