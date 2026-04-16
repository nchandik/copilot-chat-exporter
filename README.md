# Copilot Chat History Exporter

Automatically export all your VS Code Copilot chat sessions to JSON and Markdown formats daily.

## Features

✅ **Interactive Setup** — First time asks where to save & what time to export  
✅ **Timezone-Aware** — Support for IST, EST, CST, MST, PST (and others)  
✅ **Extracts from all local VS Code Copilot chat sessions**  
✅ **Consolidates into clean JSON and Markdown formats**  
✅ **Portable** — works on any Windows system with VS Code  
✅ **Easy scheduling** via Windows Task Scheduler  
✅ **No external dependencies** — uses Python stdlib only  

## Quick Start

### 1. Clone or Download

```bash
git clone <repo> copilot-chat-exporter
cd copilot-chat-exporter
```

### 2. First Time Setup (Interactive)

Run the interactive setup to configure your preferences:

```bash
python export_copilot_history.py --setup
```

You'll be asked:
- **Where to save chat history files?** (default: `Documents\Copilot-History`)
- **What time to export daily?** (default: 23:00 / 11:00 PM)
  - Consider your timezone (IST, EST, CST, MST, PST)
- **What's your timezone?** (for reference only)

Your preferences are saved to: `~\.copilot_exporter_config.json`

### 3. Schedule with Windows Task Scheduler

**Option A: Using the batch file (easiest)**

1. Right-click `schedule_daily.bat`
2. Select **"Run as administrator"**
3. The task will be created automatically ✅

**Option B: Using PowerShell**

1. Right-click PowerShell
2. Select **"Run as Administrator"**
3. Run: `.\schedule_daily.ps1`

**Option C: Manual setup**

1. Open **Task Scheduler** (Press `Win + R`, type `taskschd.msc`)
2. Click **Create Basic Task**
3. Name: `Copilot Chat History Export`
4. Trigger: **Daily** at `23:00` (or your preferred time)
5. Action: **Start a program**
   - Program: `C:\path\to\python.exe`
   - Arguments: `C:\path\to\export_copilot_history.py`
6. Click **OK**

---

## Usage

### Command Line

```bash
# Run interactive setup (first time)
python export_copilot_history.py --setup

# Export today's history (uses saved config)
python export_copilot_history.py

# Export to specific directory (overrides config)
python export_copilot_history.py --output-dir "C:\My\Output\Path"

# Export a specific past date
python export_copilot_history.py --date 2026-04-15

# Reconfigure preferences
python export_copilot_history.py --setup

# Show help
python export_copilot_history.py --help
```

### Output Format

**JSON** (`prompt_response_history_YYYY-MM-DD.json`):
```json
{
  "date": "2026-04-16",
  "sessionFilesCount": 4,
  "historyCount": 65,
  "history": [
    {
      "role": "user",
      "message": "your prompt here",
      "sourceSession": "session-id",
      "source": "kind0.requests.message",
      "timestamp": 1234567890
    },
    ...
  ]
}
```

**Markdown** (`prompt_response_history_YYYY-MM-DD.md`):
```markdown
# Prompt & Response History - 2026-04-16

### Entry 1 — USER

**Source Session:** `session-id`

**Details:** kind0.requests.message

your prompt here

---

### Entry 2 — ASSISTANT

...
```

## Configuration File

Your preferences are saved to: **`~\.copilot_exporter_config.json`**

Example config:
```json
{
  "output_dir": "C:\\Users\\YourUsername\\Documents\\Copilot-History",
  "export_time": "23:00",
  "timezone": "IST",
  "created_at": "2026-04-16T10:30:45.123456",
  "version": "1.0"
}
```

To reconfigure at any time, run:
```bash
python export_copilot_history.py --setup
```

## How It Works

The script:

1. **Loads or creates config** (first run asks for preferences)
2. **Finds today's session files** in `%APPDATA%\Code\User\workspaceStorage\*\chatSessions\*.jsonl`
3. **Parses JSONL format** to extract:
   - User prompts (from `kind0` request snapshots and `kind1` metadata)
   - Assistant responses (from `kind0` response arrays and `kind2` streaming chunks)
4. **Deduplicates** identical entries
5. **Exports** consolidated history to JSON and Markdown
6. **Saves** to configured directory with today's date in filename

## Troubleshooting

**"First time setup required"**
→ This is normal! Run `python export_copilot_history.py --setup` first.

**"No session files found"**
→ Ensure VS Code has been used today (chat sessions must exist for today's date).

**"APPDATA environment variable not set"**
→ This is very rare on Windows. Check your system environment variables.

**"Permission denied" errors**
→ Run as Administrator (right-click Command Prompt → Run as administrator)

**Output files not created**
→ Check that the output directory is writable
→ Try specifying an absolute path instead of relative path

**Task Scheduler not running the export**
→ Right-click the task in Task Scheduler and select "Run" to test manually
→ Check Task Scheduler logs for errors

## File Locations

The script automatically finds:

**VS Code sessions:**
```
C:\Users\YourUsername\AppData\Roaming\Code\User\workspaceStorage\
```

**Config file:**
```
C:\Users\YourUsername\.copilot_exporter_config.json
```

**Output files:**
```
[YourConfiguredDirectory]\prompt_response_history_YYYY-MM-DD.json
[YourConfiguredDirectory]\prompt_response_history_YYYY-MM-DD.md
```

## Sharing with Colleagues

1. **Create a repo** (GitHub, GitLab, etc.) with these files
2. **Have colleagues clone it** to their machines
3. **Each person runs:**
   ```bash
   python export_copilot_history.py --setup
   ```
4. **Then:**
   ```bash
   schedule_daily.bat (as Administrator)
   ```
   Or:
   ```bash
   .\schedule_daily.ps1 (in PowerShell, as Administrator)
   ```

Done! Each team member will have their own config and daily exports based on their timezone.

## Requirements

- Windows 10 or later
- Python 3.7+
- VS Code with Copilot Chat enabled
- No pip packages needed (uses only Python stdlib)

## License

Feel free to modify and share.

---

**Questions?** Check the `QUICKSTART.md` or run:
```bash
python export_copilot_history.py --help
```
