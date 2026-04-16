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
                return json.load(f)
        except Exception:
            return None
    return None


def save_config(config):
    """Save configuration to file."""
    config_file = get_config_file()
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"⚠ Warning: Could not save config: {e}")
        return False


def interactive_setup():
    """Interactive first-time setup."""
    print("\n" + "="*50)
    print("🎉 Welcome to Copilot Chat History Exporter!")
    print("="*50)
    print("\nLet's set up your preferences for the first time.\n")

    # Ask for output directory
    print("1️⃣  Where should we save your chat history files?")
    print("   (Press Enter for default: Documents\\Copilot-History)")
    
    default_output = os.path.join(str(Path.home()), "Documents", "Copilot-History")
    user_output = input("   Path: ").strip()
    
    if not user_output:
        output_dir = default_output
    else:
        output_dir = user_output

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Ask for export time (timezone aware)
    print("\n2️⃣  What time should we export your chat history?")
    print("   (Consider your timezone)")
    print("   • Indian Standard Time (IST): 18:00 = 6:00 PM")
    print("   • US Eastern Time (EST): 18:00 = 6:00 PM")
    print("   • US Pacific Time (PST): 18:00 = 6:00 PM")
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
            print("   ⚠ Invalid format. Using default: 23:00")
            export_time = "23:00"

    # Ask for timezone info (for reference only)
    print("\n3️⃣  What's your timezone?")
    print("   • IST (Indian Standard Time, UTC+5:30)")
    print("   • EST (US Eastern, UTC-5)")
    print("   • CST (US Central, UTC-6)")
    print("   • MST (US Mountain, UTC-7)")
    print("   • PST (US Pacific, UTC-8)")
    print("   (For reference only, no impact on export time)")
    
    timezone_input = input("   Timezone: ").strip().upper()
    
    if timezone_input not in ["IST", "EST", "CST", "MST", "PST"]:
        timezone_input = "IST"

    config = {
        "output_dir": output_dir,
        "export_time": export_time,
        "timezone": timezone_input,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

    # Save config
    save_config(config)

    print("\n" + "="*50)
    print("✅ Setup complete!")
    print("="*50)
    print(f"\nYour preferences:")
    print(f"  📁 Output directory: {output_dir}")
    print(f"  🕐 Export time: {export_time} daily ({timezone_input})")
    print(f"\nConfig saved to: {get_config_file()}")
    print("\n⏭️  Next step: Set up Windows Task Scheduler")
    print("   Run: schedule_daily.bat (as Administrator)")
    print("   Or:  schedule_daily.ps1 (in PowerShell, as Administrator)")

    return config


def reconfigure():
    """Allow user to reconfigure settings."""
    existing = load_config()
    if existing:
        print(f"\n📋 Current config:")
        print(f"  Output dir: {existing.get('output_dir')}")
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
        print(f"⚠ Workspace root not found: {workspace_root}")
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
        print(f"⚠ Error reading {filepath}: {e}")
        return entries

    objs = []
    for line in lines:
        try:
            objs.append(json.loads(line))
        except Exception:
            pass

    # Pass 1: kind 0 (explicit request snapshots)
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

    # Pass 2: kind 1 (rendered user prompts from metadata)
    for idx, obj in enumerate(objs, 1):
        if not isinstance(obj, dict) or obj.get("kind") != 1:
            continue
        v = obj.get("v")
        if not isinstance(v, dict):
            continue
        md = v.get("metadata")
        if not isinstance(md, dict):
            continue
        rum = md.get("renderedUserMessage")
        if not (isinstance(rum, list) and rum and isinstance(rum[0], dict)):
            continue
        txt = rum[0].get("text")
        if not isinstance(txt, str) or not txt.strip():
            continue

        m = user_req_re.search(txt)
        if m:
            prompt = clean_text(m.group(1))
        else:
            prompt = clean_text(txt)

        if prompt:
            entries.append({
                "role": "user",
                "message": prompt,
                "sourceSession": session_id,
                "source": "kind1.metadata.renderedUserMessage",
                "line": idx,
            })

    # Pass 3: kind 2 (streamed assistant chunks)
    for idx, obj in enumerate(objs, 1):
        if not isinstance(obj, dict) or obj.get("kind") != 2:
            continue
        v = obj.get("v")
        if not isinstance(v, list):
            continue
        for chunk in v:
            if not isinstance(chunk, dict):
                continue
            val = chunk.get("value")
            if isinstance(val, str):
                c = clean_text(val)
                # Filter out tool/file operation messages
                if c and not any(c.startswith(s) for s in ("Reading [](", "Running `", "Creating [](", "Created [](")):
                    entries.append({
                        "role": "assistant",
                        "message": c,
                        "sourceSession": session_id,
                        "source": "kind2.v[].value",
                        "line": idx,
                        "requestId": chunk.get("requestId"),
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
    output_file = os.path.join(output_dir, f"prompt_response_history_{target_date}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
    return output_file


def export_to_markdown(entries, target_date, output_dir):
    """Export consolidated history to Markdown."""
    md_content = f"""# Prompt & Response History - {target_date}

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

        md_content += f"""### Entry {i} — {role}

**Source Session:** `{source_session}`

**Details:** {entry.get('source', 'N/A')}

{message}

---

"""

    output_file = os.path.join(output_dir, f"prompt_response_history_{target_date}.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    return output_file


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
        "--setup",
        action="store_true",
        help="Run interactive setup (reconfigure preferences)",
    )
    args = parser.parse_args()

    # Handle setup mode
    if args.setup:
        interactive_setup()
        return

    # Load or create config
    config = load_config()
    if config is None:
        print("\n🔧 First time setup required...\n")
        config = interactive_setup()

    # Determine target date
    if args.date:
        target_date = args.date
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Invalid date format: {target_date}. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")

    # Determine output directory (command-line arg overrides config)
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = config.get("output_dir", os.getcwd())

    os.makedirs(output_dir, exist_ok=True)

    print(f"📅 Exporting Copilot chat history for {target_date}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🕐 Configured export time: {config.get('export_time')} ({config.get('timezone')})")

    # Find session files
    try:
        session_files = find_session_files(target_date)
    except Exception as e:
        print(f"❌ Error finding session files: {e}")
        sys.exit(1)

    if not session_files:
        print(f"⚠ No session files found for {target_date}")
        print(f"  (Searched in: {get_workspace_storage_root()})")
        return

    print(f"✅ Found {len(session_files)} session file(s)")

    # Parse all session files
    all_entries = []
    for filepath in session_files:
        print(f"  • Parsing {os.path.basename(filepath)}...")
        entries = parse_session_file(filepath)
        all_entries.extend(entries)

    print(f"📝 Total entries before dedup: {len(all_entries)}")

    # Deduplicate
    final_entries = deduplicate_entries(all_entries)
    print(f"✂️  After dedup: {len(final_entries)} entries")

    # Export
    try:
        json_file = export_to_json(final_entries, session_files, target_date, output_dir)
        print(f"✅ JSON: {json_file}")

        md_file = export_to_markdown(final_entries, target_date, output_dir)
        print(f"✅ Markdown: {md_file}")

        print(f"\n🎉 Export complete!")
    except Exception as e:
        print(f"❌ Error exporting: {e}")
        sys.exit(1)



if __name__ == "__main__":
    main()
