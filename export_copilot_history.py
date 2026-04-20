#!/usr/bin/env python3
"""
VS Code Copilot Chat History Exporter

Daily automation script to extract and consolidate all VS Code Copilot chat sessions
from the local workspaceStorage into JSON and Markdown formats.

Usage:
  python export_copilot_history.py [--output-dir OUTPUT_DIR] [--date YYYY-MM-DD] [--setup]

Environment:
  - First run: interactive setup to configure output directory and export time
  - Subsequent runs: uses saved config (~/.copilot_exporter_config.json)
  - Can override with --output-dir flag
"""

import json
import os
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path


OUTPUT_FILE_PREFIX = "chat_history"
RUN_MODE_AUTOMATIC = "automatic"
RUN_MODE_MANUAL = "manual"


# ===================== CONFIG MANAGEMENT =====================

def get_config_file():
    """Get the path to the config file in user's home directory."""
    home = str(Path.home())
    return os.path.join(home, ".copilot_exporter_config.json")


def load_config():
    """Load saved configuration."""
    config_file = get_config_file()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                return normalize_config(loaded)
        except Exception:
            return None
    return None


def normalize_config(config):
    """Normalize config fields and backfill defaults for older versions."""
    if not isinstance(config, dict):
        return None

    normalized = dict(config)
    run_mode = str(normalized.get("run_mode", RUN_MODE_AUTOMATIC)).strip().lower()
    if run_mode not in (RUN_MODE_AUTOMATIC, RUN_MODE_MANUAL):
        run_mode = RUN_MODE_AUTOMATIC
    normalized["run_mode"] = run_mode

    if run_mode == RUN_MODE_AUTOMATIC:
        export_time = normalized.get("export_time")
        if not isinstance(export_time, str) or not export_time.strip():
            normalized["export_time"] = "23:00"
    else:
        normalized["export_time"] = None

    timezone = normalized.get("timezone")
    if not isinstance(timezone, str) or not timezone.strip():
        normalized["timezone"] = "IST"

    if "version" not in normalized:
        normalized["version"] = "1.1"

    return normalized


def save_config(config):
    """Save configuration to file."""
    config_file = get_config_file()
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"[WARN] Warning: Could not save config: {e}")
        return False


def interactive_setup():
    """Interactive first-time setup."""
    print("\n" + "="*50)
    print("[DONE] Welcome to Copilot Chat History Exporter!")
    print("="*50)
    print("\nLet's set up your preferences for the first time.\n")

    # Ask for output directory
    print("[1]  Where should we save your chat history files?")
    print("   (Press Enter for default: Documents\\Copilot-History)")
    
    default_output = os.path.join(str(Path.home()), "Documents", "Copilot-History")
    user_output = input("   Path: ").strip()
    
    if not user_output:
        output_dir = default_output
    else:
        output_dir = user_output

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Ask for run mode
    print("\n[2]  How do you want to run exports?")
    print("     1) Automatic daily (scheduled)")
    print("     2) Manual on demand")
    print("   (Press Enter for default: 1)")

    user_mode = input("   Mode (1/2): ").strip()
    if user_mode in ("", "1"):
        run_mode = RUN_MODE_AUTOMATIC
    elif user_mode == "2":
        run_mode = RUN_MODE_MANUAL
    else:
        print("   [WARN] Invalid choice. Using default: Automatic daily")
        run_mode = RUN_MODE_AUTOMATIC

    export_time = None
    if run_mode == RUN_MODE_AUTOMATIC:
        # Ask for export time (timezone aware)
        print("\n[3]  What time should we export your chat history?")
        print("   (Consider your timezone)")
        print("     • Indian Standard Time (IST): 18:00 = 6:00 PM")
        print("     • US Eastern Time (EST): 18:00 = 6:00 PM")
        print("     • US Pacific Time (PST): 18:00 = 6:00 PM")
        print("   (Enter in 24-hour format, e.g., 18:00 for 6:00 PM)")
        print("   (Press Enter for default: 23:00 / 11:00 PM)")

        user_time = input("   Time (HH:MM): ").strip()

        if not user_time:
            export_time = "23:00"
        else:
            # Validate time format
            try:
                datetime.strptime(user_time, "%H:%M")
                export_time = user_time
            except ValueError:
                print("   [WARN] Invalid format. Using default: 23:00")
                export_time = "23:00"

    # Ask for timezone info (for reference only)
    question_num = "4" if run_mode == RUN_MODE_AUTOMATIC else "3"
    print(f"\n[{question_num}]  What's your timezone?")
    print("     • IST (Indian Standard Time, UTC+5:30)")
    print("     • EST (US Eastern, UTC-5)")
    print("     • CST (US Central, UTC-6)")
    print("     • MST (US Mountain, UTC-7)")
    print("     • PST (US Pacific, UTC-8)")
    print("   (For reference only, no impact on export time)")
    
    timezone_input = input("   Timezone: ").strip().upper()
    
    if timezone_input not in ["IST", "EST", "CST", "MST", "PST"]:
        timezone_input = "IST"

    config = {
        "output_dir": output_dir,
        "export_time": export_time,
        "run_mode": run_mode,
        "timezone": timezone_input,
        "created_at": datetime.now().isoformat(),
        "version": "1.1"
    }

    # Save config
    save_config(config)

    print("\n" + "="*50)
    print("[OK] Setup complete!")
    print("="*50)
    print(f"\nYour preferences:")
    print(f"  [DIR] Output directory: {output_dir}")
    print(f"  [MODE] Run mode: {run_mode}")
    if run_mode == RUN_MODE_AUTOMATIC:
        print(f"  [TIME] Export time: {export_time} daily ({timezone_input})")
    else:
        print(f"  [TIME] Manual mode (no scheduled time)")
    print(f"\nConfig saved to: {get_config_file()}")
    if run_mode == RUN_MODE_AUTOMATIC:
        print("\n[SKIP]  Next step: Set up Windows Task Scheduler")
        print("   Run: schedule_daily.bat (as Administrator)")
        print("   Or:  schedule_daily.ps1 (in PowerShell, as Administrator)")
    else:
        print("\n[SKIP]  Next step: Run exports manually when needed")
        print("   Run: python export_copilot_history.py")
        print("   Manual mode lets you export today or previous dates during each run")

    return config


def reconfigure():
    """Allow user to reconfigure settings."""
    existing = load_config()
    if existing:
        print(f"\n Current config:")
        print(f"  Output dir: {existing.get('output_dir')}")
        print(f"  Run mode: {existing.get('run_mode', RUN_MODE_AUTOMATIC)}")
        print(f"  Export time: {existing.get('export_time')}")
        print(f"  Timezone: {existing.get('timezone')}")
        confirm = input("\nReconfigure? (y/n): ").strip().lower()
        if confirm != 'y':
            return existing
    
    return interactive_setup()


def get_workspace_storage_root():
    """Get the VS Code workspaceStorage root path."""
    appdata = os.getenv("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not set")
    return os.path.join(appdata, "Code", "User", "workspaceStorage")


def find_session_files(target_date, workspace_root=None):
    """Find all .jsonl session files modified on target_date."""
    if workspace_root is None:
        workspace_root = get_workspace_storage_root()

    if not os.path.isdir(workspace_root):
        print(f"[WARN] Workspace root not found: {workspace_root}")
        return []

    session_files = []
    for dirpath, _, filenames in os.walk(workspace_root):
        if dirpath.endswith("chatSessions"):
            for name in filenames:
                if name.endswith(".jsonl"):
                    full_path = os.path.join(dirpath, name)
                    try:
                        mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d")
                        if mtime == target_date:
                            session_files.append(full_path)
                    except (OSError, ValueError):
                        pass
    return sorted(session_files)


def clean_text(s):
    """Normalize and clean text content."""
    s = s.replace("\r\n", "\n").replace("\r", "\n").strip()
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def extract_assistant_response(resp):
    """Extract assistant text from various response formats."""
    texts = []
    if isinstance(resp, list):
        for item in resp:
            if not isinstance(item, dict):
                continue
            v = item.get("value")
            if isinstance(v, str) and v.strip():
                texts.append(clean_text(v))
            c = item.get("content")
            if isinstance(c, dict):
                for key in ("value", "text"):
                    cv = c.get(key)
                    if isinstance(cv, str) and cv.strip():
                        texts.append(clean_text(cv))
    elif isinstance(resp, dict):
        for key in ("value", "text", "message"):
            v = resp.get(key)
            if isinstance(v, str) and v.strip():
                texts.append(clean_text(v))
    elif isinstance(resp, str) and resp.strip():
        texts.append(clean_text(resp))

    out = []
    seen = set()
    for t in texts:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return "\n\n".join(out).strip()


def parse_session_file(filepath):
    """Parse a single JSONL session file."""
    user_req_re = re.compile(r"<userRequest>\s*(.*?)\s*</userRequest>", re.IGNORECASE | re.DOTALL)
    entries = []
    session_id = os.path.basename(filepath).replace(".jsonl", "")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[WARN] Error reading {filepath}: {e}")
        return entries

    objs = []
    for line in lines:
        try:
            objs.append(json.loads(line))
        except Exception:
            pass

    # Primary: kind 1 — contains interleaved user prompt + assistant response via toolCallRounds
    # Each kind1 object represents one complete conversation turn (prompt + response pair).
    for idx, obj in enumerate(objs, 1):
        if not isinstance(obj, dict) or obj.get("kind") != 1:
            continue
        v = obj.get("v")
        if not isinstance(v, dict):
            continue
        md = v.get("metadata")
        if not isinstance(md, dict):
            continue

        # Extract user prompt
        rum = md.get("renderedUserMessage")
        user_text = ""
        if isinstance(rum, list) and rum and isinstance(rum[0], dict):
            txt = rum[0].get("text", "")
            if isinstance(txt, str) and txt.strip():
                m = user_req_re.search(txt)
                user_text = clean_text(m.group(1) if m else txt)

        if user_text:
            entries.append({
                "role": "user",
                "message": user_text,
                "sourceSession": session_id,
                "source": "kind1.renderedUserMessage",
                "line": idx,
            })

        # Extract assistant response from toolCallRounds — last non-empty round response is the final answer
        tc_rounds = md.get("toolCallRounds", [])
        response_parts = []
        for rnd in tc_rounds:
            if not isinstance(rnd, dict):
                continue
            resp = rnd.get("response")
            if isinstance(resp, str) and resp.strip():
                response_parts.append(clean_text(resp))

        if response_parts:
            # Combine all rounds into one complete response
            full_response = "\n\n".join(response_parts)
            entries.append({
                "role": "assistant",
                "message": full_response,
                "sourceSession": session_id,
                "source": "kind1.toolCallRounds.response",
                "line": idx,
            })

    # Fallback: kind 0 — used only if kind1 produced no entries (older session format)
    if not entries:
        for obj in objs:
            if not isinstance(obj, dict) or obj.get("kind") != 0:
                continue
            v = obj.get("v")
            if not isinstance(v, dict):
                continue
            reqs = v.get("requests")
            if not isinstance(reqs, list):
                continue
            for req in reqs:
                if not isinstance(req, dict):
                    continue
                msg = req.get("message")
                user_text = ""
                if isinstance(msg, dict) and isinstance(msg.get("text"), str):
                    user_text = clean_text(msg.get("text"))
                elif isinstance(msg, str):
                    user_text = clean_text(msg)
                if user_text:
                    entries.append({
                        "role": "user",
                        "message": user_text,
                        "sourceSession": session_id,
                        "source": "kind0.requests.message",
                        "requestId": req.get("requestId"),
                        "timestamp": req.get("timestamp"),
                    })
                assistant_text = extract_assistant_response(req.get("response"))
                if assistant_text:
                    entries.append({
                        "role": "assistant",
                        "message": assistant_text,
                        "sourceSession": session_id,
                        "source": "kind0.requests.response",
                        "requestId": req.get("requestId"),
                        "timestamp": req.get("timestamp"),
                    })

    return entries


def deduplicate_entries(entries):
    """Deduplicate exact repeats while preserving order."""
    seen = set()
    final = []
    for h in entries:
        key = (h.get("role"), h.get("message"), h.get("sourceSession"), h.get("source"))
        if key in seen:
            continue
        seen.add(key)
        final.append(h)
    return final


def export_to_json(entries, session_files, target_date, output_dir):
    """Export consolidated history to JSON."""
    payload = {
        "date": target_date,
        "note": "Best-effort extraction from VS Code Copilot chat session files modified on this date.",
        "sessionFilesCount": len(session_files),
        "sessionFiles": session_files,
        "historyCount": len(entries),
        "history": entries,
    }
    output_file = os.path.join(output_dir, f"{OUTPUT_FILE_PREFIX}_{target_date}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
    return output_file


def export_to_markdown(entries, target_date, output_dir):
    """Export consolidated history to Markdown."""
    md_content = f"""# Chat History - {target_date}

**Date:** {target_date}

**Total Sessions:** {len(set(e.get('sourceSession') for e in entries))}

**Total Entries:** {len(entries)}

---

## Notes

Best-effort extraction from VS Code Copilot chat session files modified on this date.

---

## Conversation History

"""

    for i, entry in enumerate(entries, 1):
        role = entry['role'].upper()
        message = entry['message']
        source_session = entry.get('sourceSession', 'N/A')

        md_content += f"""### Entry {i} - {role}

**Source Session:** `{source_session}`

**Details:** {entry.get('source', 'N/A')}

{message}

---

"""

    output_file = os.path.join(output_dir, f"{OUTPUT_FILE_PREFIX}_{target_date}.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    return output_file


# ===================== DATE HANDLING & INTERACTIVE PROMPTS =====================

def calculate_date_from_days_ago(days_ago, timezone=None):
    """Calculate target date by subtracting days from today."""
    if days_ago < 0:
        raise ValueError("days_ago must be >= 0")
    
    target = datetime.now() - timedelta(days=days_ago)
    return target.strftime("%Y-%m-%d")


def parse_custom_date(date_str):
    """Parse and validate a custom date string."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # Check if date is in the future
        if dt > datetime.now():
            raise ValueError("Date is in the future")
        return dt.strftime("%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date: {e}")


def interactive_date_picker():
    """Interactive prompt to select export date."""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)
    week_ago = today - timedelta(days=7)
    
    print("\n" + "="*60)
    print("[DATE] Which date would you like to export?")
    print("="*60)
    print(f"\n  1) Today ({today.strftime('%Y-%m-%d')})")
    print(f"  2) Yesterday ({yesterday.strftime('%Y-%m-%d')})")
    print(f"  3) Two days ago ({two_days_ago.strftime('%Y-%m-%d')})")
    print(f"  4) One week ago ({week_ago.strftime('%Y-%m-%d')})")
    print(f"  5) Custom date (enter YYYY-MM-DD)")
    print(f"\nEnter your choice (1-5): ", end="")
    
    while True:
        choice = input().strip()
        
        if choice == "1":
            return today.strftime("%Y-%m-%d")
        elif choice == "2":
            return yesterday.strftime("%Y-%m-%d")
        elif choice == "3":
            return two_days_ago.strftime("%Y-%m-%d")
        elif choice == "4":
            return week_ago.strftime("%Y-%m-%d")
        elif choice == "5":
            print("Enter date (YYYY-MM-DD): ", end="")
            custom = input().strip()
            try:
                return parse_custom_date(custom)
            except ValueError as e:
                print(f"[ERROR] {e}")
                print("Enter date (YYYY-MM-DD): ", end="")
                continue
        else:
            print("[ERROR] Invalid choice. Please enter 1-5: ", end="")
            continue


def check_file_exists_and_prompt(output_dir, target_date, non_interactive=False):
    """Check if export files exist and prompt user for action."""
    json_file = os.path.join(output_dir, f"{OUTPUT_FILE_PREFIX}_{target_date}.json")
    md_file = os.path.join(output_dir, f"{OUTPUT_FILE_PREFIX}_{target_date}.md")
    
    if os.path.exists(json_file) or os.path.exists(md_file):
        if non_interactive:
            print(f"[INFO] Existing files found for {target_date}; overwriting in non-interactive mode")
            return True

        print(f"\n[WARN]  Files already exist for {target_date}")
        if os.path.exists(json_file):
            print(f"     • {os.path.basename(json_file)}")
        if os.path.exists(md_file):
            print(f"     • {os.path.basename(md_file)}")
        
        while True:
            print("\nWhat would you like to do?")
            print("  (O)verwrite  (C)ancel: ", end="")
            choice = input().strip().lower()
            
            if choice in ("o", "overwrite"):
                return True
            elif choice in ("c", "cancel"):
                return False
            else:
                print("[ERROR] Invalid choice. Enter 'o' or 'c': ", end="")
                continue
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Export VS Code Copilot chat history to JSON and Markdown"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (overrides config)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Target date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--days-ago",
        type=int,
        default=None,
        help="Export date N days ago (0=today, 1=yesterday, etc.)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=None,
        help="Export last N days in one go (e.g., --batch 7 for last week)",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run interactive setup (reconfigure preferences)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Force interactive mode (prompts for date/overwrite)",
    )
    parser.add_argument(
        "--scheduled",
        action="store_true",
        help="Force non-interactive scheduled mode (defaults to today, overwrites existing files)",
    )
    args = parser.parse_args()

    if args.interactive and args.scheduled:
        print("[ERROR] --interactive and --scheduled cannot be used together")
        sys.exit(1)

    # Handle setup mode
    if args.setup:
        interactive_setup()
        return

    # Load or create config
    config = load_config()
    if config is None:
        print("\n[SETUP] First time setup required...\n")
        config = interactive_setup()

    run_mode = config.get("run_mode", RUN_MODE_AUTOMATIC)
    if args.interactive:
        run_mode = RUN_MODE_MANUAL
    elif args.scheduled:
        run_mode = RUN_MODE_AUTOMATIC

    is_non_interactive = run_mode == RUN_MODE_AUTOMATIC

    # Validate command line arguments
    if args.days_ago is not None and args.days_ago < 0:
        print(f"[ERROR] days-ago must be >= 0 (got {args.days_ago})")
        sys.exit(1)
    
    if args.batch is not None and args.batch < 1:
        print(f"[ERROR] batch must be >= 1 (got {args.batch})")
        sys.exit(1)

    # Determine target dates
    target_dates = []
    
    if args.batch:
        # Export last N days
        for i in range(args.batch):
            target_dates.append(calculate_date_from_days_ago(i))
    elif args.days_ago is not None:
        # Export specific days ago
        target_dates.append(calculate_date_from_days_ago(args.days_ago))
    elif args.date:
        # Export specific date (validate format and ensure not in future)
        try:
            validated_date = parse_custom_date(args.date)
            target_dates.append(validated_date)
        except ValueError as e:
            print(f"[ERROR] {e}")
            sys.exit(1)
    else:
        if is_non_interactive:
            # Automatic mode defaults to today's date without prompts.
            target_dates.append(calculate_date_from_days_ago(0))
        else:
            # Manual mode prompts for target date.
            target_dates.append(interactive_date_picker())

    # Determine output directory (command-line arg overrides config)
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = config.get("output_dir", os.getcwd())

    os.makedirs(output_dir, exist_ok=True)

    # Process each date
    total_exported = 0
    for target_date in target_dates:
        print(f"\n{'='*60}")
        print(f"[DATE] Exporting Copilot chat history for {target_date}")
        print(f"{'='*60}")
        print(f"[DIR] Output directory: {output_dir}")
        if is_non_interactive:
            print(f"[MODE] Scheduled/non-interactive")
            print(f"[TIME] Task Scheduler trigger time is the source of truth")
        else:
            print(f"[MODE] Manual/interactive")
        print(f"[TIME] Configured export time: {config.get('export_time')} ({config.get('timezone')})")

        # Check if files exist
        if not check_file_exists_and_prompt(output_dir, target_date, non_interactive=is_non_interactive):
            print(f"[SKIP]  Skipping {target_date}")
            continue

        # Find session files
        try:
            session_files = find_session_files(target_date)
        except Exception as e:
            print(f"[ERROR] Error finding session files: {e}")
            continue

        if not session_files:
            print(f"[WARN] No session files found for {target_date}")
            print(f"  (Searched in: {get_workspace_storage_root()})")
            continue

        print(f"[OK] Found {len(session_files)} session file(s)")

        # Parse all session files
        all_entries = []
        for filepath in session_files:
            print(f"    • Parsing {os.path.basename(filepath)}...")
            entries = parse_session_file(filepath)
            all_entries.extend(entries)

        print(f"[INFO] Total entries before dedup: {len(all_entries)}")

        # Deduplicate
        final_entries = deduplicate_entries(all_entries)
        print(f"[DEDUP]  After dedup: {len(final_entries)} entries")

        # Export
        try:
            json_file = export_to_json(final_entries, session_files, target_date, output_dir)
            print(f"[OK] JSON: {json_file}")

            md_file = export_to_markdown(final_entries, target_date, output_dir)
            print(f"[OK] Markdown: {md_file}")

            total_exported += 1
        except Exception as e:
            print(f"[ERROR] Error exporting: {e}")
            continue

    if total_exported > 0:
        print(f"\n{'='*60}")
        print(f"[DONE] Export complete! ({total_exported} date(s) exported)")
        print(f"{'='*60}")
    else:
        print(f"\n[WARN] No dates were exported")
        sys.exit(1)



if __name__ == "__main__":
    main()
