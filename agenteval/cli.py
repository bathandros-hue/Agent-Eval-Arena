"""Compare agent-produced JSON traces against a fixed, transparent task suite."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .grader import evaluate


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline agent-trace evaluator")
    parser.add_argument("--scenarios", type=Path, required=True)
    parser.add_argument("--traces", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    scenarios = json.loads(args.scenarios.read_text(encoding="utf-8"))
    trials = json.loads(args.traces.read_text(encoding="utf-8"))
    report = evaluate(scenarios, trials)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
