#!/usr/bin/env python3
"""Generate an interactive HTML review page for skill evaluation results.

Usage:
    python generate_review.py <workspace-dir> --skill-name <name> [--benchmark <path>] [--previous-workspace <path>] [--static <output-path>]

Reads eval results from the workspace directory and generates an interactive
HTML page for human review of skill outputs.
"""

import argparse
import json
import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
import tempfile


def load_eval_data(workspace_dir: Path) -> list:
    """Load all eval results from workspace directory."""
    evals = []
    for eval_dir in sorted(workspace_dir.iterdir()):
        if not eval_dir.is_dir() or eval_dir.name.startswith('.'):
            continue

        metadata_path = eval_dir / "eval_metadata.json"
        if not metadata_path.exists():
            continue

        with open(metadata_path) as f:
            metadata = json.load(f)

        eval_entry = {
            "id": metadata.get("eval_id", eval_dir.name),
            "name": metadata.get("eval_name", eval_dir.name),
            "prompt": metadata.get("prompt", ""),
            "assertions": metadata.get("assertions", []),
            "runs": {}
        }

        for run_dir in eval_dir.iterdir():
            if not run_dir.is_dir():
                continue

            run_data = {"outputs": [], "grading": None, "timing": None}

            outputs_dir = run_dir / "outputs"
            if outputs_dir.exists():
                for f in sorted(outputs_dir.iterdir()):
                    if f.name == "metrics.json":
                        continue
                    try:
                        content = f.read_text(errors='replace')
                        run_data["outputs"].append({
                            "name": f.name,
                            "content": content[:50000]  # cap at 50k chars
                        })
                    except Exception:
                        run_data["outputs"].append({
                            "name": f.name,
                            "content": f"[Binary file: {f.stat().st_size} bytes]"
                        })

            grading_path = run_dir / "grading.json"
            if grading_path.exists():
                with open(grading_path) as f:
                    run_data["grading"] = json.load(f)

            timing_path = run_dir / "timing.json"
            if timing_path.exists():
                with open(timing_path) as f:
                    run_data["timing"] = json.load(f)

            eval_entry["runs"][run_dir.name] = run_data

        evals.append(eval_entry)

    return evals


def load_previous_feedback(prev_workspace: Path) -> dict:
    """Load feedback from previous iteration."""
    feedback_path = prev_workspace / "feedback.json"
    if feedback_path.exists():
        with open(feedback_path) as f:
            data = json.load(f)
        return {r["run_id"]: r["feedback"] for r in data.get("reviews", [])}
    return {}


def load_previous_outputs(prev_workspace: Path) -> dict:
    """Load outputs from previous iteration for comparison."""
    prev_evals = load_eval_data(prev_workspace)
    prev_outputs = {}
    for ev in prev_evals:
        for run_name, run_data in ev["runs"].items():
            key = f"{ev['name']}-{run_name}"
            prev_outputs[key] = run_data.get("outputs", [])
    return prev_outputs


def generate_html(skill_name: str, evals: list, benchmark: dict = None,
                  prev_feedback: dict = None, prev_outputs: dict = None) -> str:
    """Generate the review HTML page."""

    data = {
        "skill_name": skill_name,
        "evals": evals,
        "benchmark": benchmark,
        "prev_feedback": prev_feedback or {},
        "prev_outputs": prev_outputs or {}
    }

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Skill Review: {skill_name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font: 14px/1.6 system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; }}
  .header {{ background: #1e293b; padding: 16px 24px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
  .header h1 {{ font-size: 18px; color: #f8fafc; }}
  .tabs {{ display: flex; gap: 4px; }}
  .tab {{ padding: 8px 16px; border-radius: 6px; cursor: pointer; background: #334155; color: #94a3b8; border: none; font-size: 14px; }}
  .tab.active {{ background: #3b82f6; color: #fff; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
  .nav {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
  .nav button {{ padding: 8px 16px; border-radius: 6px; cursor: pointer; background: #334155; color: #e2e8f0; border: 1px solid #475569; }}
  .nav button:hover {{ background: #475569; }}
  .eval-card {{ background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 16px; border: 1px solid #334155; }}
  .eval-card h3 {{ color: #60a5fa; margin-bottom: 8px; }}
  .prompt {{ background: #0f172a; padding: 12px; border-radius: 6px; margin-bottom: 12px; font-family: monospace; white-space: pre-wrap; }}
  .run-section {{ margin-top: 16px; }}
  .run-label {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-bottom: 8px; }}
  .run-label.with {{ background: #065f46; color: #6ee7b7; }}
  .run-label.without {{ background: #7c2d12; color: #fdba74; }}
  .output-file {{ background: #0f172a; padding: 12px; border-radius: 6px; margin: 8px 0; }}
  .output-file .filename {{ color: #94a3b8; font-size: 12px; margin-bottom: 4px; }}
  .output-file pre {{ white-space: pre-wrap; word-break: break-word; max-height: 400px; overflow-y: auto; }}
  .grading {{ margin-top: 12px; }}
  .grade {{ display: flex; align-items: center; gap: 8px; padding: 4px 0; }}
  .grade .pass {{ color: #4ade80; }}
  .grade .fail {{ color: #f87171; }}
  .feedback-box {{ width: 100%; min-height: 80px; background: #0f172a; color: #e2e8f0; border: 1px solid #475569; border-radius: 6px; padding: 12px; font: 14px/1.6 system-ui; resize: vertical; margin-top: 8px; }}
  .prev-feedback {{ background: #1a1a2e; border-left: 3px solid #6366f1; padding: 8px 12px; margin: 8px 0; font-style: italic; color: #a5b4fc; }}
  details {{ margin: 8px 0; }}
  summary {{ cursor: pointer; color: #94a3b8; padding: 4px 0; }}
  summary:hover {{ color: #e2e8f0; }}
  .submit-btn {{ padding: 12px 24px; background: #3b82f6; color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }}
  .submit-btn:hover {{ background: #2563eb; }}
  .benchmark-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
  .benchmark-table th, .benchmark-table td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #334155; }}
  .benchmark-table th {{ color: #94a3b8; font-weight: 600; }}
  .delta-positive {{ color: #4ade80; }}
  .delta-negative {{ color: #f87171; }}
  .counter {{ color: #94a3b8; font-size: 14px; }}
</style>
</head>
<body>
<div class="header">
  <h1>Skill Review: {skill_name}</h1>
  <div class="tabs">
    <button class="tab active" onclick="showTab('outputs')">Outputs</button>
    <button class="tab" onclick="showTab('benchmark')">Benchmark</button>
  </div>
</div>

<div class="container" id="outputs-tab">
  <div class="nav">
    <button onclick="prevEval()">&larr; Previous</button>
    <span class="counter" id="counter">1 / 1</span>
    <button onclick="nextEval()">Next &rarr;</button>
  </div>
  <div id="eval-container"></div>
  <div style="text-align:center;margin-top:24px;">
    <button class="submit-btn" onclick="submitReviews()">Submit All Reviews</button>
  </div>
</div>

<div class="container" id="benchmark-tab" style="display:none;">
  <div id="benchmark-container"></div>
</div>

<script>
const DATA = {json.dumps(data)};
let currentIdx = 0;
const feedbackStore = {{}};

function showTab(tab) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('outputs-tab').style.display = tab === 'outputs' ? 'block' : 'none';
  document.getElementById('benchmark-tab').style.display = tab === 'benchmark' ? 'block' : 'none';
}}

function renderEval(idx) {{
  const ev = DATA.evals[idx];
  if (!ev) return;
  document.getElementById('counter').textContent = `${{idx + 1}} / ${{DATA.evals.length}}`;
  let html = `<div class="eval-card"><h3>${{ev.name}}</h3><div class="prompt">${{escHtml(ev.prompt)}}</div>`;

  for (const [runName, runData] of Object.entries(ev.runs)) {{
    const isWith = runName.includes('with_skill');
    const labelClass = isWith ? 'with' : 'without';
    const label = runName.replace(/_/g, ' ');
    html += `<div class="run-section"><span class="run-label ${{labelClass}}">${{label}}</span>`;

    for (const out of runData.outputs || []) {{
      html += `<div class="output-file"><div class="filename">${{out.name}}</div><pre>${{escHtml(out.content)}}</pre></div>`;
    }}

    if (runData.grading) {{
      html += `<details><summary>Formal Grades (${{runData.grading.summary?.passed || 0}}/${{runData.grading.summary?.total || 0}} passed)</summary><div class="grading">`;
      for (const exp of runData.grading.expectations || []) {{
        const cls = exp.passed ? 'pass' : 'fail';
        const icon = exp.passed ? '&#10003;' : '&#10007;';
        html += `<div class="grade"><span class="${{cls}}">${{icon}}</span> ${{escHtml(exp.text)}} <small style="color:#64748b">— ${{escHtml(exp.evidence || '')}}</small></div>`;
      }}
      html += `</div></details>`;
    }}

    const prevKey = `${{ev.name}}-${{runName}}`;
    const prevOut = DATA.prev_outputs[prevKey];
    if (prevOut && prevOut.length) {{
      html += `<details><summary>Previous Output</summary>`;
      for (const out of prevOut) {{
        html += `<div class="output-file"><div class="filename">${{out.name}}</div><pre>${{escHtml(out.content)}}</pre></div>`;
      }}
      html += `</details>`;
    }}

    const runId = `${{ev.name}}-${{runName}}`;
    const prevFb = DATA.prev_feedback[runId];
    if (prevFb) {{
      html += `<div class="prev-feedback">Previous feedback: ${{escHtml(prevFb)}}</div>`;
    }}

    html += `<textarea class="feedback-box" data-run-id="${{runId}}" placeholder="Your feedback (leave empty if it looks good)" oninput="saveFeedback(this)">${{feedbackStore[runId] || ''}}</textarea>`;
    html += `</div>`;
  }}

  html += `</div>`;
  document.getElementById('eval-container').innerHTML = html;
}}

function saveFeedback(el) {{
  feedbackStore[el.dataset.runId] = el.value;
}}

function prevEval() {{
  if (currentIdx > 0) {{ currentIdx--; renderEval(currentIdx); }}
}}
function nextEval() {{
  if (currentIdx < DATA.evals.length - 1) {{ currentIdx++; renderEval(currentIdx); }}
}}

function escHtml(s) {{
  const div = document.createElement('div');
  div.textContent = s || '';
  return div.innerHTML;
}}

function submitReviews() {{
  const reviews = Object.entries(feedbackStore).map(([runId, feedback]) => ({{
    run_id: runId,
    feedback: feedback,
    timestamp: new Date().toISOString()
  }}));
  const blob = new Blob([JSON.stringify({{ reviews, status: 'complete' }}, null, 2)], {{ type: 'application/json' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'feedback.json';
  a.click();
  alert('Feedback downloaded! Move the file to the workspace directory and tell Claude you are done.');
}}

function renderBenchmark() {{
  const bm = DATA.benchmark;
  if (!bm) {{
    document.getElementById('benchmark-container').innerHTML = '<p style="color:#94a3b8">No benchmark data available.</p>';
    return;
  }}
  let html = `<h2 style="color:#f8fafc;margin-bottom:16px;">Benchmark: ${{bm.metadata?.skill_name || DATA.skill_name}}</h2>`;

  const summary = bm.run_summary;
  if (summary) {{
    html += `<table class="benchmark-table"><thead><tr><th>Metric</th><th>With Skill</th><th>Without Skill</th><th>Delta</th></tr></thead><tbody>`;
    for (const metric of ['pass_rate', 'time_seconds', 'tokens']) {{
      const ws = summary.with_skill?.[metric];
      const wos = summary.without_skill?.[metric];
      const delta = summary.delta?.[metric] || 'N/A';
      const deltaClass = delta.startsWith('+') && metric === 'pass_rate' ? 'delta-positive' : (delta.startsWith('-') && metric === 'pass_rate' ? 'delta-negative' : '');
      html += `<tr><td>${{metric.replace(/_/g, ' ')}}</td>`;
      html += `<td>${{ws ? `${{ws.mean?.toFixed(2)}} ± ${{ws.stddev?.toFixed(2)}}` : 'N/A'}}</td>`;
      html += `<td>${{wos ? `${{wos.mean?.toFixed(2)}} ± ${{wos.stddev?.toFixed(2)}}` : 'N/A'}}</td>`;
      html += `<td class="${{deltaClass}}">${{delta}}</td></tr>`;
    }}
    html += `</tbody></table>`;
  }}

  if (bm.notes?.length) {{
    html += `<h3 style="color:#94a3b8;margin-top:24px;">Analyst Notes</h3><ul>`;
    for (const note of bm.notes) {{
      html += `<li style="margin:8px 0;">${{escHtml(note)}}</li>`;
    }}
    html += `</ul>`;
  }}

  document.getElementById('benchmark-container').innerHTML = html;
}}

// Keyboard navigation
document.addEventListener('keydown', e => {{
  if (e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'ArrowLeft') prevEval();
  if (e.key === 'ArrowRight') nextEval();
}});

renderEval(0);
renderBenchmark();
</script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Generate skill evaluation review page")
    parser.add_argument("workspace", help="Path to workspace iteration directory")
    parser.add_argument("--skill-name", required=True, help="Skill name")
    parser.add_argument("--benchmark", help="Path to benchmark.json")
    parser.add_argument("--previous-workspace", help="Path to previous iteration workspace")
    parser.add_argument("--static", help="Write standalone HTML to this path instead of starting server")
    parser.add_argument("--port", type=int, default=8247, help="Port for HTTP server")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    if not workspace.exists():
        print(f"Error: workspace {workspace} does not exist", file=sys.stderr)
        sys.exit(1)

    evals = load_eval_data(workspace)
    benchmark = None
    if args.benchmark and Path(args.benchmark).exists():
        with open(args.benchmark) as f:
            benchmark = json.load(f)

    prev_feedback = {}
    prev_outputs = {}
    if args.previous_workspace:
        prev_ws = Path(args.previous_workspace)
        if prev_ws.exists():
            prev_feedback = load_previous_feedback(prev_ws)
            prev_outputs = load_previous_outputs(prev_ws)

    html = generate_html(args.skill_name, evals, benchmark, prev_feedback, prev_outputs)

    if args.static:
        out_path = Path(args.static)
        out_path.write_text(html)
        print(f"Written to {out_path.absolute()}")
        return

    # Write HTML and serve it
    tmpdir = Path(tempfile.mkdtemp())
    index = tmpdir / "index.html"
    index.write_text(html)

    # Also write a feedback handler
    feedback_target = workspace / "feedback.json"

    os.chdir(tmpdir)
    server = HTTPServer(('localhost', args.port), SimpleHTTPRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://localhost:{args.port}"
    print(f"Review server running at {url}")
    print(f"Feedback will be saved to {feedback_target}")
    webbrowser.open(url)

    try:
        thread.join()
    except KeyboardInterrupt:
        server.shutdown()
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
