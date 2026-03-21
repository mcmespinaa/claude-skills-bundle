#!/usr/bin/env python3
"""
GHL Social MCP Server — Functional Test Runner

Calls real MCP tools against the live GHL API and reports pass/fail.
Designed for pre-release validation and smoke testing.

Usage:
    python3 qa_test_runner.py                    # full suite
    python3 qa_test_runner.py --smoke            # one test per tool
    python3 qa_test_runner.py --section posts    # one section
    python3 qa_test_runner.py --skip-destructive # skip delete/send
    python3 qa_test_runner.py --dry-run          # show plan only
    python3 qa_test_runner.py --json             # JSON output
"""

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
# Walk up to project root (qa-test/scripts/ -> qa-test/ -> skills/ -> .claude/ -> project root)
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
# MCP server lives in a separate repo (github.com/mcmespinaa/ghl-social-mcp-server)
MCP_SERVER_DIR = Path.home() / "ghl-social-mcp-server"

# Add MCP server to path so we can import tools directly
sys.path.insert(0, str(MCP_SERVER_DIR))


# ---------------------------------------------------------------------------
# Test result tracking
# ---------------------------------------------------------------------------
class TestResult:
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

    def __init__(self, name, status, message="", duration_ms=0):
        self.name = name
        self.status = status
        self.message = message
        self.duration_ms = duration_ms


class TestRunner:
    def __init__(self, args):
        self.args = args
        self.results = {}  # section -> [TestResult]
        self.cleanup_tasks = []  # (description, callable)
        self.test_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.verbose = args.verbose

    def run_test(self, section, name, fn, skip_reason=None):
        """Run a single test, catching exceptions."""
        if skip_reason:
            self.results.setdefault(section, []).append(
                TestResult(name, TestResult.SKIP, skip_reason)
            )
            return None

        if self.args.dry_run:
            self.results.setdefault(section, []).append(
                TestResult(name, TestResult.SKIP, "dry-run")
            )
            return None

        start = time.time()
        try:
            result = fn()
            elapsed = int((time.time() - start) * 1000)
            self.results.setdefault(section, []).append(
                TestResult(name, TestResult.PASS, duration_ms=elapsed)
            )
            if self.verbose:
                print(f"  PASS  {name} ({elapsed}ms)")
            return result
        except AssertionError as e:
            elapsed = int((time.time() - start) * 1000)
            self.results.setdefault(section, []).append(
                TestResult(name, TestResult.FAIL, str(e), elapsed)
            )
            if self.verbose:
                print(f"  FAIL  {name}: {e}")
            return None
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            raw = f"{type(e).__name__}: {e}"
            # Clean up long error messages (e.g. Cloudflare HTML pages)
            # Strip HTML, collapse whitespace, truncate
            clean = raw.replace("\n", " ").replace("\r", " ")
            if "<" in clean:
                clean = clean[:clean.index("<")].strip() or clean[:120]
            msg = clean[:200] + "..." if len(clean) > 200 else clean
            self.results.setdefault(section, []).append(
                TestResult(name, TestResult.ERROR, msg, elapsed)
            )
            if self.verbose:
                print(f"  ERROR {name}: {msg}")
                if self.args.verbose:
                    traceback.print_exc()
            return None

    # -----------------------------------------------------------------------
    # Prerequisites
    # -----------------------------------------------------------------------
    def check_prerequisites(self):
        """Check env vars and config files. Returns dict of available features."""
        avail = {
            "ghl": bool(os.environ.get("GHL_API_KEY") and os.environ.get("GHL_LOCATION_ID")),
            "youtube": bool(os.environ.get("YOUTUBE_API_KEY")),
            "notebooklm": False,
            "locations_json": (PROJECT_ROOT / "locations.json").exists(),
            "accounts_map": (PROJECT_ROOT / "ghl_accounts_map.json").exists(),
            "post_log": (PROJECT_ROOT / "ghl_post_log.md").exists(),
            "mcp_server": MCP_SERVER_DIR.exists(),
        }

        # Check notebooklm CLI
        try:
            import subprocess
            r = subprocess.run(["notebooklm", "--version"], capture_output=True, timeout=5)
            avail["notebooklm"] = r.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return avail

    # -----------------------------------------------------------------------
    # Section: validation (no API calls)
    # -----------------------------------------------------------------------
    def test_validation(self, smoke=False):
        """Test validate_caption tool."""
        from tools.validation import register_validation_tools
        from tests.conftest import MockMCP

        mcp = MockMCP()
        register_validation_tools(mcp)
        validate = mcp.tools["validate_caption"]

        def t_valid_caption():
            r = validate(caption="Morning clarity hits different.", platforms=["instagram"])
            assert r["passed"] is True, f"Expected passed=True, got {r}"

        def t_em_dash():
            r = validate(caption="This is great \u2014 really great.", platforms=[])
            assert r["passed"] is False, "Em dash should fail"
            assert any("em dash" in e.lower() or "—" in e for e in r["errors"]), f"Expected em dash error: {r['errors']}"

        def t_banned_word():
            r = validate(caption="Let me delve into this topic.", platforms=[])
            assert r["passed"] is False, "Banned word 'delve' should fail"

        def t_banned_phrase():
            r = validate(caption="Let me shed light on this important matter.", platforms=[])
            assert r["passed"] is False, "Banned phrase should fail"

        def t_soft_words_ok():
            r = validate(caption="This can maybe work.", platforms=[])
            assert r["passed"] is True, "2 soft words should pass"

        def t_soft_words_warn():
            r = validate(caption="This can maybe just really work out.", platforms=[])
            assert len(r.get("warnings", [])) > 0, "3+ soft words should warn"

        def t_twitter_limit():
            r = validate(caption="x" * 281, platforms=["twitter"])
            assert r["passed"] is False, "281 chars should fail for Twitter"

        def t_twitter_ok():
            r = validate(caption="x" * 280, platforms=["twitter"])
            assert r["char_counts"]["twitter"]["ok"] is True, "280 chars should pass for Twitter"

        def t_ig_no_media():
            r = validate(caption="Hello.", platforms=["instagram"], has_media=False)
            assert r["passed"] is False, "IG without media should fail"

        def t_tiktok_no_media():
            r = validate(caption="Hello.", platforms=["tiktok"], has_media=False)
            assert r["passed"] is False, "TikTok without media should fail"

        def t_fb_no_media_ok():
            r = validate(caption="Hello.", platforms=["facebook"], has_media=False)
            assert r["passed"] is True, "FB text-only should pass"

        def t_char_counts():
            r = validate(caption="Test post.", platforms=["facebook", "instagram", "linkedin"])
            assert "char_counts" in r, "Should include char_counts"
            assert "facebook" in r["char_counts"], "Should include facebook counts"

        tests = [
            ("valid caption passes", t_valid_caption),
            ("em dash detected", t_em_dash),
            ("banned word detected", t_banned_word),
            ("banned phrase detected", t_banned_phrase),
            ("2 soft words ok", t_soft_words_ok),
            ("3+ soft words warn", t_soft_words_warn),
            ("twitter 281 chars fails", t_twitter_limit),
            ("twitter 280 chars ok", t_twitter_ok),
            ("IG requires media", t_ig_no_media),
            ("TikTok requires media", t_tiktok_no_media),
            ("FB text-only ok", t_fb_no_media_ok),
            ("char counts included", t_char_counts),
        ]

        if smoke:
            tests = tests[:3]

        for name, fn in tests:
            self.run_test("validation", name, fn)

    # -----------------------------------------------------------------------
    # Section: scheduling (reads local file only)
    # -----------------------------------------------------------------------
    def test_scheduling(self, smoke=False):
        """Test get_next_slot tool."""
        from tools.scheduling import register_scheduling_tools
        from tests.conftest import MockMCP
        import tempfile

        # Use a temp dir as project root to avoid touching real post log
        with tempfile.TemporaryDirectory() as tmp:
            mcp = MockMCP()
            register_scheduling_tools(mcp, str(MCP_SERVER_DIR), tmp)
            get_slot = mcp.tools["get_next_slot"]

            def t_default_slot():
                r = get_slot()
                assert r.endswith("Z"), f"Should end with Z: {r}"
                assert "T" in r, f"Should contain T: {r}"

            def t_format():
                r = get_slot()
                # Should be valid ISO 8601
                assert len(r) == 20, f"Expected 20-char ISO 8601, got {len(r)}: {r}"

            def t_with_log():
                log = Path(tmp) / "ghl_post_log.md"
                log.write_text("| test | FB | 2026-06-01T09:00:00Z | post_1 | scheduled | |\n")
                r = get_slot()
                assert r == "2026-06-02T09:00:00Z", f"Expected 24h later, got {r}"

            def t_skips_deleted():
                log = Path(tmp) / "ghl_post_log.md"
                log.write_text(
                    "| test | FB | 2026-06-05T09:00:00Z | post_2 | deleted | |\n"
                    "| test | FB | 2026-06-01T09:00:00Z | post_1 | scheduled | |\n"
                )
                r = get_slot()
                assert r == "2026-06-02T09:00:00Z", f"Should skip deleted, got {r}"

            def t_empty_log():
                log = Path(tmp) / "ghl_post_log.md"
                log.write_text("")
                r = get_slot()
                assert r.endswith("Z"), f"Empty log should return default slot: {r}"

            def t_no_log_file():
                log = Path(tmp) / "ghl_post_log.md"
                if log.exists():
                    log.unlink()
                r = get_slot()
                assert r.endswith("Z"), f"Missing log should return default slot: {r}"

            tests = [
                ("default slot format", t_default_slot),
                ("ISO 8601 format", t_format),
                ("24h after last post", t_with_log),
                ("skips deleted entries", t_skips_deleted),
                ("empty log returns default", t_empty_log),
                ("missing log returns default", t_no_log_file),
            ]

            if smoke:
                tests = tests[:2]

            for name, fn in tests:
                self.run_test("scheduling", name, fn)

    # -----------------------------------------------------------------------
    # Section: resources (read-only)
    # -----------------------------------------------------------------------
    def test_resources(self, smoke=False):
        """Test MCP resources."""
        from resources.providers import register_resources
        from tests.conftest import MockMCP

        mcp = MockMCP()
        register_resources(mcp, str(PROJECT_ROOT))

        def t_platform_limits():
            r = mcp.resources["platform://limits"]()
            assert "Facebook" in r, "Should contain Facebook"
            assert "Instagram" in r, "Should contain Instagram"
            assert "63,206" in r, "Should contain FB char limit"

        def t_post_log():
            r = mcp.resources["post://log"]()
            assert isinstance(r, str), "Should return string"

        def t_accounts_map():
            r = mcp.resources["accounts://map"]()
            assert isinstance(r, str), "Should return string"

        def t_locations_config():
            r = mcp.resources["locations://config"]()
            assert isinstance(r, str), "Should return string"

        def t_content_plan():
            r = mcp.resources["plan://current"]()
            assert isinstance(r, str), "Should return string"

        def t_resource_count():
            assert len(mcp.resources) == 5, f"Expected 5 resources, got {len(mcp.resources)}"

        tests = [
            ("platform limits content", t_platform_limits),
            ("post log readable", t_post_log),
            ("accounts map readable", t_accounts_map),
            ("locations config readable", t_locations_config),
            ("content plan readable", t_content_plan),
            ("5 resources registered", t_resource_count),
        ]

        if smoke:
            tests = tests[:2]

        for name, fn in tests:
            self.run_test("resources", name, fn)

    # -----------------------------------------------------------------------
    # Section: accounts (live API — read-only)
    # -----------------------------------------------------------------------
    def test_accounts(self, avail, smoke=False):
        """Test account and contact tools against live API."""
        skip = None if avail["ghl"] else "GHL_API_KEY not set"

        from tools.accounts import register_account_tools
        from tests.conftest import MockMCP

        mcp = MockMCP()
        register_account_tools(mcp, str(MCP_SERVER_DIR), str(PROJECT_ROOT))
        get_accounts = mcp.tools["get_accounts"]
        search_contacts = mcp.tools["search_contacts"]

        def t_get_accounts():
            r = get_accounts()
            assert isinstance(r, dict), f"Expected dict, got {type(r)}"

        def t_get_accounts_location():
            r = get_accounts(location="")  # default location
            assert isinstance(r, dict), f"Expected dict, got {type(r)}"

        def t_invalid_location():
            try:
                get_accounts(location="bad location!")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_search_by_tag():
            r = search_contacts(tag="newsletter")
            assert "contacts" in r, f"Expected 'contacts' key: {r.keys()}"
            assert "count" in r, f"Expected 'count' key: {r.keys()}"

        def t_search_no_params():
            try:
                search_contacts()
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_search_tag_too_long():
            try:
                search_contacts(tag="x" * 201)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_search_limit_clamp():
            # Should not raise — limit clamped to 10000
            r = search_contacts(tag="test", limit=99999)
            assert isinstance(r, dict), "Should return dict even with large limit"

        tests = [
            ("get_accounts returns dict", t_get_accounts),
            ("get_accounts default location", t_get_accounts_location),
            ("invalid location raises", t_invalid_location),
            ("search contacts by tag", t_search_by_tag),
            ("search no params raises", t_search_no_params),
            ("search tag too long raises", t_search_tag_too_long),
            ("search limit clamped", t_search_limit_clamp),
        ]

        if smoke:
            tests = tests[:2]

        for name, fn in tests:
            self.run_test("accounts", name, fn, skip_reason=skip)

    # -----------------------------------------------------------------------
    # Section: posts (live API — creates/deletes posts)
    # -----------------------------------------------------------------------
    def test_posts(self, avail, smoke=False):
        """Test post CRUD against live API."""
        skip = None if avail["ghl"] else "GHL_API_KEY not set"

        from tools.posts import register_post_tools
        from tests.conftest import MockMCP

        mcp = MockMCP()
        register_post_tools(mcp, str(MCP_SERVER_DIR), str(PROJECT_ROOT))
        create_post = mcp.tools["create_post"]
        get_post = mcp.tools["get_post"]
        update_post = mcp.tools["update_post"]
        delete_post = mcp.tools["delete_post"]

        # We need a valid account ID — read from accounts map
        account_id = None
        try:
            acct_file = PROJECT_ROOT / "ghl_accounts_map.json"
            if acct_file.exists():
                acct_data = json.loads(acct_file.read_text())
                for _, loc_data in acct_data.items():
                    if not isinstance(loc_data, dict):
                        continue
                    # Support both flat ({FB: {id:...}}) and nested ({accounts: {FB: {id:...}}})
                    platforms = loc_data.get("accounts", loc_data)
                    if isinstance(platforms, dict):
                        for _, info in platforms.items():
                            if isinstance(info, dict) and "id" in info:
                                account_id = info["id"]
                                break
                    if account_id:
                        break
        except Exception:
            pass

        if not account_id:
            skip = "No account_id found in ghl_accounts_map.json"

        # Schedule 7 days out
        future = datetime.now(timezone.utc) + timedelta(days=7)
        schedule_date = future.strftime("%Y-%m-%dT10:00:00Z")
        test_caption = f"QA test post - safe to delete. Created at {self.test_timestamp}."
        created_post_id = None

        # Read user_id from locations.json (supports nested "locations" key)
        user_id = ""
        try:
            loc_file = PROJECT_ROOT / "locations.json"
            if loc_file.exists():
                loc_data = json.loads(loc_file.read_text())
                locs = loc_data.get("locations", loc_data)
                default_key = loc_data.get("default", "")
                if default_key and default_key in locs:
                    user_id = locs[default_key].get("userId", "")
        except Exception:
            pass

        def t_create():
            nonlocal created_post_id
            r = create_post(
                account_id=account_id,
                caption=test_caption,
                schedule_date=schedule_date,
                user_id=user_id,
            )
            assert isinstance(r, dict), f"Expected dict, got {type(r)}"
            # Extract post ID — GHL nests it at results.post._id
            post_id = (
                r.get("id")
                or r.get("postId")
                or r.get("results", {}).get("post", {}).get("_id")
                or r.get("_id")
            )
            assert post_id, f"No post ID in response: {list(r.keys())}"
            created_post_id = post_id
            self.cleanup_tasks.append(("delete test post", lambda: delete_post(post_id=post_id)))

        def t_empty_caption():
            try:
                create_post(account_id=account_id, caption="", schedule_date=schedule_date)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_invalid_account_id():
            try:
                create_post(account_id="bad id!", caption="test", schedule_date=schedule_date)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_invalid_date():
            try:
                create_post(account_id=account_id, caption="test", schedule_date="not-a-date")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_invalid_media_type():
            try:
                create_post(
                    account_id=account_id, caption="test",
                    schedule_date=schedule_date,
                    media_urls="https://example.com/test.pdf",
                    media_types="pdf",
                )
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_get():
            if not created_post_id:
                raise AssertionError("No post to get (create failed)")
            r = get_post(post_id=created_post_id)
            assert isinstance(r, dict), f"Expected dict, got {type(r)}"

        def t_invalid_post_id():
            try:
                get_post(post_id="bad id!")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_update_caption():
            if not created_post_id:
                raise AssertionError("No post to update (create failed)")
            r = update_post(
                post_id=created_post_id,
                caption=f"Updated QA test - {self.test_timestamp}",
            )
            assert isinstance(r, dict), f"Expected dict, got {type(r)}"

        def t_update_no_changes():
            try:
                update_post(post_id=created_post_id or "dummy")
                assert False, "Should have raised ValueError (no changes)"
            except ValueError:
                pass

        def t_delete():
            if not created_post_id:
                raise AssertionError("No post to delete (create failed)")
            r = delete_post(post_id=created_post_id)
            assert isinstance(r, dict), f"Expected dict, got {type(r)}"
            # Remove from cleanup since we just deleted it
            self.cleanup_tasks = [(d, f) for d, f in self.cleanup_tasks if "test post" not in d]

        tests = [
            ("create post", t_create),
            ("empty caption raises", t_empty_caption),
            ("invalid account_id raises", t_invalid_account_id),
            ("invalid schedule_date raises", t_invalid_date),
            ("invalid media_type raises", t_invalid_media_type),
            ("get post", t_get),
            ("invalid post_id raises", t_invalid_post_id),
            ("update caption", t_update_caption),
            ("update no changes raises", t_update_no_changes),
        ]

        if not self.args.skip_destructive:
            tests.append(("delete post", t_delete))

        if smoke:
            tests = [tests[0], tests[1]]  # create + validation

        for name, fn in tests:
            self.run_test("posts", name, fn, skip_reason=skip)

    # -----------------------------------------------------------------------
    # Section: youtube (live API — read-only)
    # -----------------------------------------------------------------------
    def test_youtube(self, avail, smoke=False):
        """Test YouTube tools against live API."""
        skip = None if avail["youtube"] else "YOUTUBE_API_KEY not set"

        from tools.youtube import register_youtube_tools
        from tests.conftest import MockMCP

        yt_scripts = str(PROJECT_ROOT / ".claude" / "skills" / "yt-search" / "scripts")
        mcp = MockMCP()
        register_youtube_tools(mcp, yt_scripts, str(PROJECT_ROOT))
        yt_search = mcp.tools["youtube_search"]
        yt_transcript = mcp.tools["youtube_transcript"]
        yt_channel = mcp.tools["youtube_channel_analysis"]

        def t_search():
            r = yt_search(query="MCP server tutorial", max_results=2)
            assert isinstance(r, (dict, list)), f"Expected dict or list, got {type(r)}"

        def t_search_no_params():
            try:
                yt_search()
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_search_invalid_type():
            try:
                yt_search(query="test", search_type="invalid")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_search_invalid_order():
            try:
                yt_search(query="test", order="invalid")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_search_query_too_long():
            try:
                yt_search(query="x" * 2001)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_transcript():
            # Use a known public video with captions
            r = yt_transcript(video_id="dQw4w9WgXcQ")
            assert isinstance(r, dict), f"Expected dict, got {type(r)}"

        def t_transcript_no_params():
            try:
                yt_transcript()
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_transcript_invalid_lang():
            try:
                yt_transcript(video_id="abc123", language="123")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_channel():
            r = yt_channel(handle="mkbhd")
            assert isinstance(r, dict), f"Expected dict, got {type(r)}"

        def t_channel_no_params():
            try:
                yt_channel()
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        def t_channel_invalid_id():
            try:
                yt_channel(channel_id="bad id!")
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        tests = [
            ("search by query", t_search),
            ("search no params raises", t_search_no_params),
            ("search invalid type raises", t_search_invalid_type),
            ("search invalid order raises", t_search_invalid_order),
            ("search query too long raises", t_search_query_too_long),
            ("transcript by video_id", t_transcript),
            ("transcript no params raises", t_transcript_no_params),
            ("transcript invalid lang raises", t_transcript_invalid_lang),
            ("channel analysis", t_channel),
            ("channel no params raises", t_channel_no_params),
            ("channel invalid id raises", t_channel_invalid_id),
        ]

        if smoke:
            tests = [tests[0], tests[5], tests[8]]

        for name, fn in tests:
            self.run_test("youtube", name, fn, skip_reason=skip)

    # -----------------------------------------------------------------------
    # Report
    # -----------------------------------------------------------------------
    def print_report(self):
        """Print summary table."""
        if self.args.json:
            self._print_json()
            return

        total_pass = total_fail = total_skip = total_error = 0

        print("\n" + "=" * 60)
        print("GHL Social MCP Server — QA Test Results")
        print("=" * 60)
        print(f"\n{'Section':<20} {'Tests':>5} {'Pass':>5} {'Fail':>5} {'Skip':>5} {'Err':>5}")
        print("-" * 60)

        # Use insertion-ordered keys so report matches execution order
        for section in self.results:
            results = self.results.get(section, [])
            if not results:
                continue
            p = sum(1 for r in results if r.status == TestResult.PASS)
            f = sum(1 for r in results if r.status == TestResult.FAIL)
            s = sum(1 for r in results if r.status == TestResult.SKIP)
            e = sum(1 for r in results if r.status == TestResult.ERROR)
            total_pass += p
            total_fail += f
            total_skip += s
            total_error += e
            print(f"{section:<20} {len(results):>5} {p:>5} {f:>5} {s:>5} {e:>5}")

        total = total_pass + total_fail + total_skip + total_error
        print("-" * 60)
        print(f"{'TOTAL':<20} {total:>5} {total_pass:>5} {total_fail:>5} {total_skip:>5} {total_error:>5}")
        print()

        # Print failures
        failures = []
        for section, results in self.results.items():
            for r in results:
                if r.status in (TestResult.FAIL, TestResult.ERROR):
                    failures.append((section, r))

        if failures:
            print("FAILURES:")
            for section, r in failures:
                print(f"  [{section}] {r.name}: {r.message}")
            print()
            print(f"Result: FAIL ({len(failures)} failure(s))")
        else:
            print(f"Result: {'ALL PASSED' if total_fail == 0 and total_error == 0 else 'PASS'}")

        return total_fail + total_error

    def _print_json(self):
        """Print results as JSON."""
        output = {}
        for section, results in self.results.items():
            output[section] = [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "duration_ms": r.duration_ms,
                }
                for r in results
            ]
        print(json.dumps(output, indent=2))

    def cleanup(self):
        """Run cleanup tasks (delete test posts, etc.)."""
        if self.args.dry_run:
            return
        for desc, fn in self.cleanup_tasks:
            try:
                fn()
                if self.verbose:
                    print(f"  Cleanup: {desc} - OK")
            except Exception as e:
                if self.verbose:
                    print(f"  Cleanup: {desc} - FAILED: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="GHL Social MCP Server — QA Test Runner")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test (one test per tool)")
    parser.add_argument("--section", type=str, help="Run one section only")
    parser.add_argument("--skip-destructive", action="store_true", help="Skip delete/send operations")
    parser.add_argument("--dry-run", action="store_true", help="Show test plan without executing")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--verbose", action="store_true", help="Show request/response details")
    args = parser.parse_args()

    runner = TestRunner(args)

    # Check prerequisites
    avail = runner.check_prerequisites()

    if not avail["mcp_server"]:
        print(f"ERROR: MCP server not found at {MCP_SERVER_DIR}", file=sys.stderr)
        sys.exit(2)

    if not args.json:
        print(f"QA Test Runner — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project root: {PROJECT_ROOT}")
        print(f"MCP server: {MCP_SERVER_DIR}")
        print(f"GHL API: {'available' if avail['ghl'] else 'NOT AVAILABLE'}")
        print(f"YouTube API: {'available' if avail['youtube'] else 'not available'}")
        print(f"NotebookLM: {'available' if avail['notebooklm'] else 'not available'}")
        print()

    sections = {
        "validation": lambda: runner.test_validation(smoke=args.smoke),
        "scheduling": lambda: runner.test_scheduling(smoke=args.smoke),
        "resources": lambda: runner.test_resources(smoke=args.smoke),
        "accounts": lambda: runner.test_accounts(avail, smoke=args.smoke),
        "posts": lambda: runner.test_posts(avail, smoke=args.smoke),
        "youtube": lambda: runner.test_youtube(avail, smoke=args.smoke),
    }

    if args.section:
        if args.section not in sections:
            print(f"Unknown section: {args.section}. Available: {', '.join(sections.keys())}")
            sys.exit(2)
        sections = {args.section: sections[args.section]}

    for section_name, section_fn in sections.items():
        if not args.json:
            print(f"--- {section_name} ---")
        try:
            section_fn()
        except Exception as e:
            print(f"  Section {section_name} crashed: {e}", file=sys.stderr)
            if args.verbose:
                traceback.print_exc()

    # Report
    failure_count = runner.print_report()

    # Cleanup
    if runner.cleanup_tasks:
        if not args.json:
            print("\nCleaning up test artifacts...")
        runner.cleanup()

    sys.exit(1 if failure_count else 0)


if __name__ == "__main__":
    main()
