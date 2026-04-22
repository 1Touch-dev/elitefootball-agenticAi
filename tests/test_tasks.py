import unittest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from app.main import app
from app.tasks.schemas import TaskSubmissionRequest


@patch('app.tasks.service.celery_app.send_task')
@patch('app.tasks.service.route_task')
class TestTaskRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.submission_request = TaskSubmissionRequest(
            task_kind="run_analysis",
            payload={"example_key": "example_value"},
            requested_by="test_suite",
        )

    def test_create_task_success(self, mock_route_task, mock_send_task):
        mock_route_task.return_value = ["analyst"]
        mock_send_task.return_value = MagicMock(id="mock_task_id")

        response = self.client.post("/tasks", json=self.submission_request.dict())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["task_id"], "mock_task_id")

    def test_create_task_queue_unavailable(self, mock_route_task, mock_send_task):
        mock_send_task.side_effect = RuntimeError("Queue unavailable")

        response = self.client.post("/tasks", json=self.submission_request.dict())
        self.assertEqual(response.status_code, 503)
