#!/usr/bin/env python3
"""Eval runner: orchestrates deterministic checks + LLM judge + golden set.

Usage:
    python3 eval_runner.py                          # Full eval (all golden set)
    python3 eval_runner.py --caption "text" --platform linkedin
    python3 eval_runner.py --deterministic-only      # Skip LLM judge
    python3 eval_runner.py --skill post              # Filter golden set
    python3 eval_runner.py --json                    # Machine-readable output
    python3 eval_runner.py --verbose                 # Per-check details
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
GOLDEN_SET_PATH = SKILL_DIR / "references" / "golden-set.json"

# Import sibling modules
sys.path.insert(0, str(SCRIPT_DIR))
from deterministic_checks import run_all as run_deterministic, score as det_score
from llm_judge import judge as llm_judge


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------

def letter_grade(score: float) -> str:
    if score >= 95:
        return "A+"
    elif score >= 90:
        return "A"
    elif score >= 80:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "F"


# ---------------------------------------------------------------------------
# Single caption evaluation
# ---------------------------------------------------------------------------

def evaluate_caption(
    caption: str,
    platform: str,
    is_carousel: bool = False,
    deterministic_only: bool = False,
    verbose: bool = False,
) -> dict:
    """Evaluate a single caption. Returns structured result dict."""

    # Deterministic checks
    det_results = run_deterministic(caption, platform=platform, is_carousel=is_carousel)
    d_score = det_score(det_results)

    result = {
        "deterministic_score": round(d_score, 1),
        "deterministic_checks": [
            {
                "id": r.check_id,
                "name": r.name,
                "passed": r.passed,
                "detail": r.detail,
            }
            for r in det_results
        ],
    }

    if deterministic_only:
        result["composite_score"] = round(d_score, 1)
        result["grade"] = letter_grade(d_score)
        result["mode"] = "deterministic-only"
    else:
        # LLM judge
        try:
            judge_result = llm_judge(caption, platform)
            j_score = judge_result.weighted_score()
            composite = 0.4 * d_score + 0.6 * j_score

            result["llm_judge_score"] = round(j_score, 1)
            result["llm_judge_scores"] = judge_result.scores
            result["llm_judge_rationales"] = judge_result.rationales
            result["composite_score"] = round(composite, 1)
            result["grade"] = letter_grade(composite)
            result["mode"] = "full"
        except (ValueError, RuntimeError) as e:
            # API key missing or API error — fall back to deterministic
            result["llm_judge_error"] = str(e)
            result["composite_score"] = round(d_score, 1)
            result["grade"] = letter_grade(d_score)
            result["mode"] = "deterministic-only (fallback)"

    return result


# ---------------------------------------------------------------------------
# Golden set evaluation
# ---------------------------------------------------------------------------

def load_golden_set(skill_filter: str = "") -> list[dict]:
    """Load golden set test cases, optionally filtered by skill."""
    if not GOLDEN_SET_PATH.exists():
        print(f"ERROR: Golden set not found at {GOLDEN_SET_PATH}", file=sys.stderr)
        sys.exit(2)

    with open(GOLDEN_SET_PATH) as f:
        cases = json.load(f)

    if skill_filter:
        cases = [c for c in cases if c.get("skill") == skill_filter]

    return cases


def run_golden_set(
    cases: list[dict],
    deterministic_only: bool = False,
    verbose: bool = False,
) -> list[dict]:
    """Run eval on all golden set cases."""
    results = []
    for case in cases:
        result = evaluate_caption(
            caption=case["caption"],
            platform=case.get("platform", ""),
            is_carousel=case.get("is_carousel", False),
            deterministic_only=deterministic_only,
            verbose=verbose,
        )
        result["case_id"] = case["id"]
        result["description"] = case.get("description", "")
        result["platform"] = case.get("platform", "")

        # Check against baselines
        expect_fail = case.get("expect_fail", False)
        min_det = case.get("min_deterministic", 0)
        min_comp = case.get("min_composite", 0)

        if expect_fail:
            # For expected-fail cases, check that specific checks fail
            fail_checks = set(case.get("fail_checks", []))
            failed_ids = {
                c["id"] for c in result["deterministic_checks"] if not c["passed"]
            }
            result["baseline_met"] = fail_checks.issubset(failed_ids)
            result["baseline_note"] = (
                f"Expected failures {fail_checks} {'found' if result['baseline_met'] else 'NOT found'} "
                f"in actual failures {failed_ids}"
            )
        else:
            det_ok = result["deterministic_score"] >= min_det
            comp_ok = result["composite_score"] >= min_comp
            result["baseline_met"] = det_ok and comp_ok
            if not result["baseline_met"]:
                issues = []
                if not det_ok:
                    issues.append(
                        f"det {result['deterministic_score']:.0f} < {min_det}"
                    )
                if not comp_ok:
                    issues.append(
                        f"comp {result['composite_score']:.0f} < {min_comp}"
                    )
                result["baseline_note"] = "; ".join(issues)
            else:
                result["baseline_note"] = "meets baselines"

        results.append(result)
    return results


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_caption_report(result: dict, verbose: bool = False):
    """Print human-readable report for a single caption."""
    grade = result["grade"]
    composite = result["composite_score"]
    d_score = result["deterministic_score"]
    mode = result["mode"]

    print(f"\n{'='*60}")
    print(f"  Grade: {grade}  |  Composite: {composite}/100  |  Mode: {mode}")
    print(f"{'='*60}")
    print(f"  Deterministic: {d_score}/100")

    if "llm_judge_score" in result:
        print(f"  LLM Judge:     {result['llm_judge_score']}/100")

    if "llm_judge_error" in result:
        print(f"  LLM Judge:     SKIPPED ({result['llm_judge_error'][:80]})")

    # Deterministic check details
    checks = result["deterministic_checks"]
    failed = [c for c in checks if not c["passed"]]
    passed = [c for c in checks if c["passed"]]

    if failed:
        print(f"\n  FAILED ({len(failed)}):")
        for c in failed:
            print(f"    {c['id']} {c['name']}: {c['detail']}")

    if verbose:
        print(f"\n  PASSED ({len(passed)}):")
        for c in passed:
            print(f"    {c['id']} {c['name']}: {c['detail']}")

    # LLM judge details
    if verbose and "llm_judge_scores" in result:
        print(f"\n  LLM Judge Dimensions:")
        for dim, score in result["llm_judge_scores"].items():
            rationale = result["llm_judge_rationales"].get(dim, "")
            print(f"    {dim}: {score}/5 — {rationale[:80]}")

    print()


def print_golden_report(results: list[dict], verbose: bool = False):
    """Print human-readable golden set report."""
    print(f"\n{'='*70}")
    print(f"  GOLDEN SET EVAL — {len(results)} test cases")
    print(f"{'='*70}\n")

    # Summary table
    print(f"  {'ID':<8} {'Platform':<10} {'Grade':<6} {'Comp':<6} {'Det':<6} {'Base':<6} Description")
    print(f"  {'-'*8} {'-'*10} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*30}")

    all_met = True
    for r in results:
        base_icon = "PASS" if r["baseline_met"] else "FAIL"
        if not r["baseline_met"]:
            all_met = False
        print(
            f"  {r['case_id']:<8} {r['platform']:<10} {r['grade']:<6} "
            f"{r['composite_score']:<6.0f} {r['deterministic_score']:<6.0f} "
            f"{base_icon:<6} {r['description'][:40]}"
        )

    # Totals
    baselines_met = sum(1 for r in results if r["baseline_met"])
    avg_composite = sum(r["composite_score"] for r in results) / len(results) if results else 0
    avg_det = sum(r["deterministic_score"] for r in results) / len(results) if results else 0

    print(f"\n  {'─'*70}")
    print(f"  Baselines met: {baselines_met}/{len(results)}")
    print(f"  Avg composite: {avg_composite:.1f}/100  |  Avg deterministic: {avg_det:.1f}/100")
    print(f"  Overall: {'PASS' if all_met else 'FAIL'}")
    print()

    # Verbose: per-case detail
    if verbose:
        for r in results:
            print(f"  --- {r['case_id']}: {r['description']} ---")
            print_caption_report(r, verbose=verbose)

    return all_met


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Content quality evaluator")
    parser.add_argument("--caption", help="Evaluate a single caption")
    parser.add_argument("--platform", default="linkedin", help="Target platform")
    parser.add_argument("--carousel", action="store_true", help="Treat as carousel post")
    parser.add_argument("--skill", help="Filter golden set by skill name")
    parser.add_argument(
        "--deterministic-only",
        action="store_true",
        help="Skip LLM judge (fast, free)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", action="store_true", help="Show per-check details")

    args = parser.parse_args()

    # Single caption mode
    if args.caption:
        result = evaluate_caption(
            caption=args.caption,
            platform=args.platform,
            is_carousel=args.carousel,
            deterministic_only=args.deterministic_only,
            verbose=args.verbose,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_caption_report(result, verbose=args.verbose)

        # Exit 0 if B+ or above
        sys.exit(0 if result["composite_score"] >= 80 else 1)

    # Golden set mode
    cases = load_golden_set(skill_filter=args.skill or "")
    if not cases:
        print("No test cases found.", file=sys.stderr)
        sys.exit(2)

    results = run_golden_set(
        cases,
        deterministic_only=args.deterministic_only,
        verbose=args.verbose,
    )

    if args.json:
        print(json.dumps(results, indent=2))
        all_met = all(r["baseline_met"] for r in results)
    else:
        all_met = print_golden_report(results, verbose=args.verbose)

    sys.exit(0 if all_met else 1)


if __name__ == "__main__":
    main()
