"""Deterministic content quality checks (no LLM needed).

Extracts and extends the rule-based validation from validate_ghl_post.py
into a reusable scoring module. Each check returns a CheckResult.
"""

import re
import unicodedata

# ---------------------------------------------------------------------------
# Configuration (synced with validate_ghl_post.py)
# ---------------------------------------------------------------------------

CHAR_LIMITS = {
    "facebook": 63206,
    "instagram": 2200,
    "linkedin": 3000,
    "tiktok": 2200,
    "twitter": 280,
    "x": 280,
    "gmb": 1500,
    "threads": 500,
}

EMOJI_RANGES = {
    "linkedin": (1, 2),
    "instagram": (2, 4),
    "twitter": (0, 2),
    "x": (0, 2),
    "facebook": (1, 3),
    "threads": (0, 2),
}

HARD_BANNED_PHRASES = [
    "shed light", "dive deep", "not alone", "in a world where",
    "remains to be seen", "glimpse into", "in summary", "in conclusion",
    "cutting-edge", "ever-evolving",
]

HARD_BANNED_WORDS = [
    "delve", "embark", "enlightening", "esteemed", "realm", "tapestry",
    "illuminate", "unveil", "pivotal", "intricate", "elucidate", "hence",
    "furthermore", "however", "moreover", "utilize", "utilizing", "skyrocket",
    "abyss", "revolutionize", "disruptive", "groundbreaking", "remarkable",
    "inquiries", "stark", "testament", "navigating", "landscape",
    "synergy", "paradigm", "leverage", "robust", "seamless", "holistic",
    "multifaceted", "nuanced", "plethora", "myriad", "resonate",
    "transformative", "empower", "elevate", "foster", "underscore",
]

SOFT_BANNED_WORDS = [
    "can", "may", "just", "that", "very", "really", "literally", "actually",
    "certainly", "probably", "basically", "could", "maybe", "boost",
    "powerful", "exciting", "harness", "craft", "crafting", "imagine",
    "discover", "unlock",
]

SOFT_WARN_THRESHOLD = 3

_HARD_WORD_RE = {w: re.compile(r"\b" + re.escape(w) + r"\b", re.I) for w in HARD_BANNED_WORDS}
_SOFT_WORD_RE = {w: re.compile(r"\b" + re.escape(w) + r"\b", re.I) for w in SOFT_BANNED_WORDS}

# Passive voice heuristic: was/were/been/being + past-participle-like word
_PASSIVE_RE = re.compile(
    r"\b(?:was|were|been|being|is|are)\s+\w+(?:ed|en|ized|ated)\b", re.I
)

# Hashtag pattern
_HASHTAG_RE = re.compile(r"#\w+")


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(self, check_id: str, name: str, passed: bool, detail: str = ""):
        self.check_id = check_id
        self.name = name
        self.passed = passed
        self.detail = detail

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"{self.check_id} [{status}] {self.name}: {self.detail}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_emojis(text: str) -> int:
    """Count emoji characters in text."""
    count = 0
    for ch in text:
        if unicodedata.category(ch) in ("So", "Sk"):
            count += 1
        # Also catch emoji sequences (skin tones, ZWJ)
        elif ord(ch) >= 0x1F600:
            count += 1
    return count


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Split on sentence-ending punctuation followed by space or newline
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in raw if s.strip()]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def d1_em_dashes(text: str, **_) -> CheckResult:
    """No em dashes or en dashes."""
    found = []
    if "\u2014" in text:
        found.append("em dash (\u2014)")
    if "\u2013" in text:
        found.append("en dash (\u2013)")
    return CheckResult("D1", "em/en dash", not found,
                        f"Found: {', '.join(found)}" if found else "clean")


def d2_hard_banned(text: str, **_) -> CheckResult:
    """No hard-banned words or phrases."""
    found = []
    text_lower = text.lower()
    for phrase in HARD_BANNED_PHRASES:
        if phrase in text_lower:
            found.append(phrase)
    for word, pat in _HARD_WORD_RE.items():
        if pat.search(text):
            found.append(word)
    return CheckResult("D2", "hard-banned words", not found,
                        f"Found: {', '.join(found)}" if found else "clean")


def d3_soft_banned(text: str, **_) -> CheckResult:
    """Fewer than 3 soft-banned words."""
    found = []
    for word, pat in _SOFT_WORD_RE.items():
        if pat.search(text):
            found.append(word)
    ok = len(found) < SOFT_WARN_THRESHOLD
    return CheckResult("D3", "soft-banned density", ok,
                        f"{len(found)} found ({', '.join(found)})" if found else "clean")


def d4_char_limit(text: str, platform: str = "", **_) -> CheckResult:
    """Within platform character limit."""
    if not platform:
        return CheckResult("D4", "char limit", True, "no platform specified")
    limit = CHAR_LIMITS.get(platform.lower())
    if not limit:
        return CheckResult("D4", "char limit", True, f"unknown platform: {platform}")
    ok = len(text) <= limit
    return CheckResult("D4", "char limit", ok,
                        f"{len(text)}/{limit} chars" + ("" if ok else f" (over by {len(text)-limit})"))


def d5_emoji_count(text: str, platform: str = "", **_) -> CheckResult:
    """Emoji count within platform range."""
    if not platform:
        return CheckResult("D5", "emoji count", True, "no platform specified")
    emoji_range = EMOJI_RANGES.get(platform.lower())
    if not emoji_range:
        return CheckResult("D5", "emoji count", True, f"no emoji range for {platform}")
    count = _count_emojis(text)
    lo, hi = emoji_range
    ok = lo <= count <= hi
    return CheckResult("D5", "emoji count", ok,
                        f"{count} emojis (range {lo}-{hi} for {platform})")


def d6_formatting(text: str, **_) -> CheckResult:
    """No semicolons, markdown asterisks, or markdown headers."""
    issues = []
    if ";" in text:
        issues.append("semicolon")
    if re.search(r"\*\w", text) or re.search(r"\w\*", text):
        issues.append("asterisk/markdown")
    if re.search(r"^#{1,6}\s", text, re.M):
        issues.append("markdown header")
    return CheckResult("D6", "formatting", not issues,
                        f"Found: {', '.join(issues)}" if issues else "clean")


def d7_hashtags(text: str, is_carousel: bool = False, **_) -> CheckResult:
    """Hashtag policy: 0 for single posts, 3-5 for carousels."""
    tags = _HASHTAG_RE.findall(text)
    count = len(tags)
    if is_carousel:
        ok = 3 <= count <= 5
        return CheckResult("D7", "hashtags", ok,
                            f"{count} hashtags (carousel expects 3-5)")
    else:
        ok = count == 0
        return CheckResult("D7", "hashtags", ok,
                            f"{count} hashtags (single post expects 0)")


def d8_active_voice(text: str, **_) -> CheckResult:
    """Less than 10% passive voice sentences."""
    sentences = _split_sentences(text)
    if not sentences:
        return CheckResult("D8", "active voice", True, "no sentences")
    passive_count = sum(1 for s in sentences if _PASSIVE_RE.search(s))
    ratio = passive_count / len(sentences)
    ok = ratio < 0.10
    return CheckResult("D8", "active voice", ok,
                        f"{passive_count}/{len(sentences)} passive ({ratio:.0%})")


def d9_sentence_length(text: str, **_) -> CheckResult:
    """Average sentence <20 words, no sentence >35 words."""
    sentences = _split_sentences(text)
    if not sentences:
        return CheckResult("D9", "sentence length", True, "no sentences")
    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    max_len = max(lengths)
    ok = avg < 20 and max_len <= 35
    return CheckResult("D9", "sentence length", ok,
                        f"avg {avg:.1f} words, max {max_len} words")


def d10_platform_structure(text: str, platform: str = "", **_) -> CheckResult:
    """Platform-specific structure checks."""
    if not platform:
        return CheckResult("D10", "platform structure", True, "no platform specified")
    p = platform.lower()
    issues = []

    if p == "linkedin" and len(text) > 200:
        if "\n\n" not in text and "\n" not in text:
            issues.append("LinkedIn posts >200 chars should have line breaks")

    if p in ("twitter", "x"):
        if text.count("\n\n") > 1:
            issues.append("X/Twitter: keep to one idea, avoid multi-paragraph")

    if p == "threads" and len(text) > 500:
        issues.append(f"Threads: {len(text)} chars exceeds 500 limit")

    return CheckResult("D10", "platform structure", not issues,
                        "; ".join(issues) if issues else "ok")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

ALL_CHECKS = [d1_em_dashes, d2_hard_banned, d3_soft_banned, d4_char_limit,
              d5_emoji_count, d6_formatting, d7_hashtags, d8_active_voice,
              d9_sentence_length, d10_platform_structure]


def run_all(text: str, platform: str = "", is_carousel: bool = False) -> list[CheckResult]:
    """Run all deterministic checks on a caption."""
    return [check(text=text, platform=platform, is_carousel=is_carousel) for check in ALL_CHECKS]


def score(results: list[CheckResult]) -> float:
    """Calculate deterministic score (0-100)."""
    if not results:
        return 100.0
    passed = sum(1 for r in results if r.passed)
    return (passed / len(results)) * 100
