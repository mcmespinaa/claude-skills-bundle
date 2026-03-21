#!/usr/bin/env python3
"""Aggregate grading results into a benchmark summary.

Usage:
    python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>

Reads all grading.json and timing.json files from the iteration directory
and produces benchmark.json and benchmark.md summaries.
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


def mean(vals):
    return sum(vals) / len(vals) if vals else 0


def stddev(vals):
    if len(vals) < 2:
        return 0
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def collect_runs(iteration_dir: Path) -> list:
    """Walk iteration dir and collect all grading results."""
    runs = []
    for eval_dir in sorted(iteration_dir.iterdir()):
        if not eval_dir.is_dir() or eval_dir.name.startswith('.'):
            continue

        metadata_path = eval_dir / "eval_metadata.json"
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)

        for run_dir in sorted(eval_dir.iterdir()):
            if not run_dir.is_dir():
                continue

            grading_path = run_dir / "grading.json"
            timing_path = run_dir / "timing.json"

            if not grading_path.exists():
                continue

            with open(grading_path) as f:
                grading = json.load(f)

            timing = {}
            if timing_path.exists():
                with open(timing_path) as f:
                    timing = json.load(f)

            config = "with_skill" if "with_skill" in run_dir.name else "without_skill"
            if "old_skill" in run_dir.name:
                config = "without_skill"

            summary = grading.get("summary", {})
            runs.append({
                "eval_id": metadata.get("eval_id", eval_dir.name),
                "eval_name": metadata.get("eval_name", eval_dir.name),
                "configuration": config,
                "run_number": 1,
                "result": {
                    "pass_rate": summary.get("pass_rate", 0),
                    "passed": summary.get("passed", 0),
                    "failed": summary.get("failed", 0),
                    "total": summary.get("total", 0),
                    "time_seconds": timing.get("total_duration_seconds", 0),
                    "tokens": timing.get("total_tokens", 0),
                    "tool_calls": grading.get("execution_metrics", {}).get("total_tool_calls", 0),
                    "errors": grading.get("execution_metrics", {}).get("errors_encountered", 0)
                },
                "expectations": grading.get("expectations", [])
            })

    return runs


def aggregate(runs: list) -> dict:
    """Compute run_summary from runs."""
    summary = {}
    for config in ["with_skill", "without_skill"]:
        config_runs = [r for r in runs if r["configuration"] == config]
        if not config_runs:
            continue

        pass_rates = [r["result"]["pass_rate"] for r in config_runs]
        times = [r["result"]["time_seconds"] for r in config_runs if r["result"]["time_seconds"]]
        tokens = [r["result"]["tokens"] for r in config_runs if r["result"]["tokens"]]

        summary[config] = {
            "pass_rate": {"mean": round(mean(pass_rates), 3), "stddev": round(stddev(pass_rates), 3)},
            "time_seconds": {"mean": round(mean(times), 1), "stddev": round(stddev(times), 1)} if times else {"mean": 0, "stddev": 0},
            "tokens": {"mean": round(mean(tokens)), "stddev": round(stddev(tokens))} if tokens else {"mean": 0, "stddev": 0}
        }

    delta = {}
    if "with_skill" in summary and "without_skill" in summary:
        ws = summary["with_skill"]
        wos = summary["without_skill"]
        delta = {
            "pass_rate": f"{ws['pass_rate']['mean'] - wos['pass_rate']['mean']:+.2f}",
            "time_seconds": f"{ws['time_seconds']['mean'] - wos['time_seconds']['mean']:+.1f}",
            "tokens": f"{ws['tokens']['mean'] - wos['tokens']['mean']:+.0f}"
        }

    return {"run_summary": summary, "delta": delta}


def generate_markdown(benchmark: dict) -> str:
    """Generate a human-readable markdown summary."""
    lines = [f"# Benchmark: {benchmark['metadata']['skill_name']}", ""]

    summary = benchmark.get("run_summary", {})
    if summary:
        lines.append("| Metric | With Skill | Without Skill | Delta |")
        lines.append("|--------|-----------|--------------|-------|")
        for metric in ["pass_rate", "time_seconds", "tokens"]:
            ws = summary.get("with_skill", {}).get(metric, {})
            wos = summary.get("without_skill", {}).get(metric, {})
            delta = benchmark.get("delta", {}).get(metric, "N/A")
            ws_str = f"{ws.get('mean', 'N/A')} +/- {ws.get('stddev', 'N/A')}" if ws else "N/A"
            wos_str = f"{wos.get('mean', 'N/A')} +/- {wos.get('stddev', 'N/A')}" if wos else "N/A"
            lines.append(f"| {metric} | {ws_str} | {wos_str} | {delta} |")
        lines.append("")

    notes = benchmark.get("notes", [])
    if notes:
        lines.append("## Analyst Notes")
        for note in notes:
            lines.append(f"- {note}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Aggregate benchmark results")
    parser.add_argument("iteration_dir", help="Path to iteration directory")
    parser.add_argument("--skill-name", required=True, help="Skill name")
    args = parser.parse_args()

    iteration_dir = Path(args.iteration_dir)
    if not iteration_dir.exists():
        print(f"Error: {iteration_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    runs = collect_runs(iteration_dir)
    if not runs:
        print("No grading results found.", file=sys.stderr)
        sys.exit(1)

    agg = aggregate(runs)

    benchmark = {
        "metadata": {
            "skill_name": args.skill_name,
            "skill_path": str(iteration_dir.parent),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evals_run": list({r["eval_id"] for r in runs}),
            "runs_per_configuration": 1
        },
        "runs": runs,
        "run_summary": agg["run_summary"],
        "delta": agg["delta"],
        "notes": []
    }

    out_json = iteration_dir / "benchmark.json"
    with open(out_json, 'w') as f:
        json.dump(benchmark, f, indent=2)
    print(f"Written: {out_json}")

    out_md = iteration_dir / "benchmark.md"
    out_md.write_text(generate_markdown(benchmark))
    print(f"Written: {out_md}")


if __name__ == "__main__":
    main()
