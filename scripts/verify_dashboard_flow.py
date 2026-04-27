from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.e2e_dashboard_flow_support import render_validation_report, run_e2e_dashboard_flow


def main() -> int:
    result = run_e2e_dashboard_flow()
    print(render_validation_report(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
