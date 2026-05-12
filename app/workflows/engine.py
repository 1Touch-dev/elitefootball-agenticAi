import time
from typing import List, Callable
from app.orchestration.dag import LogicalDAG, TaskState

class WorkflowEngine:
    """Strategic coordination node abstracting batch processing across underlying workflow schedulers."""
    
    def __init__(self):
        self.dag_store = {}

    def register_workflow(self, name: str, steps: List[str]):
        dag = LogicalDAG(name=name)
        for idx, step in enumerate(steps):
            deps = [steps[idx-1]] if idx > 0 else []
            dag.add_step(step, depends_on=deps)
        self.dag_store[name] = dag
        return dag

    def trigger_run(self, name: str):
        """Simulates discrete unit graph activation preparing live Prefect/Airflow integration."""
        if name not in self.dag_store:
            raise ValueError("Unknown workflow")
        
        # Mock execution lifecycle
        dag = self.dag_store[name]
        for node in dag.nodes.values():
            node.state = TaskState.RUNNING
            node.started_at = time.time()
            # Execution payload placeholder
            node.state = TaskState.SUCCESS
            node.finished_at = time.time()
        return dag
