from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parents[2] / "memory"
REQUIRED_MEMORY_FILES = [
    MEMORY_DIR / "project_context.md",
    MEMORY_DIR / "architecture.md",
    MEMORY_DIR / "progress.md",
    MEMORY_DIR / "decisions.md",
]


def required_memory_paths() -> list[str]:
    return [str(path) for path in REQUIRED_MEMORY_FILES]


def memory_workflow_rule() -> str:
    return (
        "All future tasks MUST read memory before work. "
        "All future tasks MUST update memory after work."
    )
