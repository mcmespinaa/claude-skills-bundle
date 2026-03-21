"""LLM-as-judge for subjective content quality scoring.

Uses Claude API (Sonnet) to evaluate brand voice match, hook quality,
platform optimization, authenticity, CTA effectiveness, and substance.
Returns structured scores (1-5) with rationale.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCES_DIR = SCRIPT_DIR.parent / "references"
SHARED_REFS = SCRIPT_DIR.parent.parent.parent / "shared" / "references"

# Model for judging (Sonnet for cost efficiency)
JUDGE_MODEL = "claude-sonnet-4-20250514"

# Dimension weights for composite scoring
WEIGHTS = {
    "J1_brand_voice": 3,
    "J2_hook_quality": 2,
    "J3_platform_fit": 2,
    "J4_authenticity": 2,
    "J5_cta": 1,
    "J6_substance": 1,
}


class JudgeResult:
    def __init__(self, scores: dict[str, float], rationales: dict[str, str]):
        self.scores = scores       # {"J1_brand_voice": 4.0, ...}
        self.rationales = rationales  # {"J1_brand_voice": "Matches tone...", ...}

    def weighted_score(self) -> float:
        """Weighted average normalized to 0-100."""
        total = sum(self.scores.get(k, 3) * w for k, w in WEIGHTS.items())
        max_total = sum(5 * w for w in WEIGHTS.values())
        return (total / max_total) * 100

    def to_dict(self) -> dict:
        return {
            "scores": self.scores,
            "rationales": self.rationales,
            "weighted_score": round(self.weighted_score(), 1),
        }


def _load_voice_samples(platform: str) -> str:
    """Load voice samples for a platform from shared references."""
    samples_path = SHARED_REFS / "voice-samples.md"
    if not samples_path.exists():
        return ""

    content = samples_path.read_text()
    platform_headers = {
        "linkedin": "## LinkedIn Voice",
        "instagram": "## Instagram Voice",
        "twitter": "## Twitter/X Voice",
        "x": "## Twitter/X Voice",
        "facebook": "## Facebook Voice",
        "threads": "## Threads",  # may not exist yet
    }

    header = platform_headers.get(platform.lower(), "")
    if not header or header not in content:
        return content[:2000]  # fallback: first 2000 chars

    start = content.index(header)
    # Find next ## header
    next_header = content.find("\n## ", start + len(header))
    if next_header == -1:
        section = content[start:]
    else:
        section = content[start:next_header]

    return section.strip()


def _build_judge_prompt(caption: str, platform: str, voice_samples: str) -> str:
    """Build the evaluation prompt for Claude."""
    return f"""You are evaluating a social media caption for brand voice quality.

## Caption to evaluate
Platform: {platform}
```
{caption}
```

## Brand voice reference samples ({platform})
{voice_samples}

## Evaluation rubric

Score each dimension 1-5. Return ONLY valid JSON with this exact structure:
{{
  "J1_brand_voice": {{"score": N, "rationale": "..."}},
  "J2_hook_quality": {{"score": N, "rationale": "..."}},
  "J3_platform_fit": {{"score": N, "rationale": "..."}},
  "J4_authenticity": {{"score": N, "rationale": "..."}},
  "J5_cta": {{"score": N, "rationale": "..."}},
  "J6_substance": {{"score": N, "rationale": "..."}}
}}

### Dimension definitions

**J1 Brand Voice (1-5):** Does this sound like the person in the reference samples?
1 = corporate/generic, 3 = loosely matches, 5 = indistinguishable from samples

**J2 Hook Quality (1-5):** Does the opening line stop a scroller?
1 = "I want to share...", 3 = decent opening, 5 = would stop mid-scroll

**J3 Platform Fit (1-5):** Optimized for {platform}'s format and culture?
1 = wrong platform, 3 = generic, 5 = native to this platform

**J4 Authenticity (1-5):** Does this read like a real human wrote it?
1 = obvious AI, 3 = could be either, 5 = unmistakably human

**J5 CTA (1-5):** Natural, platform-appropriate call to action?
1 = no CTA or aggressive pitch, 3 = basic CTA, 5 = organic CTA that fits

**J6 Substance (1-5):** Specific, actionable insight?
1 = vague platitudes, 3 = some value, 5 = concrete takeaway

Return ONLY the JSON object. No markdown, no explanation outside the JSON."""


def judge(caption: str, platform: str) -> JudgeResult:
    """Evaluate a caption using Claude as judge.

    Requires ANTHROPIC_API_KEY environment variable.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Required for LLM judge evaluation. "
            "Use --deterministic-only to skip."
        )

    voice_samples = _load_voice_samples(platform)
    prompt = _build_judge_prompt(caption, platform, voice_samples)

    payload = json.dumps({
        "model": JUDGE_MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Claude API error ({e.code}): {body}")

    # Extract text from response
    text = ""
    for block in result.get("content", []):
        if block.get("type") == "text":
            text += block["text"]

    # Parse JSON from response (strip any markdown code fences)
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError(f"Failed to parse judge response as JSON: {text[:200]}")

    scores = {}
    rationales = {}
    for key in WEIGHTS:
        entry = data.get(key, {})
        scores[key] = float(entry.get("score", 3))
        rationales[key] = entry.get("rationale", "")

    return JudgeResult(scores, rationales)
