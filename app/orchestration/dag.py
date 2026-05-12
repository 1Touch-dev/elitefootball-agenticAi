from __future__ import annotations
import time
from enum import Enum
from typing import List, Callable, Dict, Any, Optional
from pydantic import BaseModel, Field

class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class PipelineNode(BaseModel):
    """Atom of execution within our abstract computational graph structure."""
    node_id: str
    description: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    
    state: TaskState = TaskState.PENDING
    started_at: Optional[float] = None
    finished_at: Optional[float] = None

class LogicalDAG(BaseModel):
    """Graph container anchoring step sequence preparing migration toward Airflow/Prefect."""
    name: str
    nodes: Dict[str, PipelineNode] = Field(default_factory=dict)
    
    def add_step(self, node_id: str, depends_on: List[str] = None):
        self.nodes[node_id] = PipelineNode(node_id=node_id, dependencies=depends_on or [])
