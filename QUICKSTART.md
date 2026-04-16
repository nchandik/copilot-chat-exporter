# Quick Start Guide

For colleagues who want to get started immediately.

## 3-Step Setup

### Step 1: Interactive Configuration (First Time Only)

```bash
python export_copilot_history.py --setup
```

You'll be asked:
1. **Where to save files?** → Choose directory or press Enter for default
2. **What time to export?** → Enter time like `18:00` (6:00 PM) or press Enter for `23:00`
3. **Your timezone?** → Choose: IST, EST, CST, MST, or PST

**Config is saved to:** `C:\Users\YourUsername\.copilot_exporter_config.json`

### Step 2: Test It Works

Run manually once:
```bash
python export_copilot_history.py
```

You should see:
```
📅 Exporting Copilot chat history for 2026-04-16
📁 Output directory: C:\Users\YourUsername\Documents\Copilot-History
🕐 Configured export time: 23:00 (IST)
✅ Found 2 session file(s)
...
✅ JSON: C:\Users\YourUsername\Documents\Copilot-History\prompt_response_history_2026-04-16.json
✅ Markdown: C:\Users\YourUsername\Documents\Copilot-History\prompt_response_history_2026-04-16.md

🎉 Export complete!
```

### Step 3: Schedule It (Daily Automation)

**Easiest way — Right-click and run as admin:**

```bash
schedule_daily.bat
```

**Or use PowerShell:**

```powershell
.\schedule_daily.ps1
```

Done! Your chat history will now export automatically every day at the time you chose.

---

## Verify It Was Scheduled

1. Press `Win + R`
2. Type `taskschd.msc`
3. Look for **"Copilot Chat History Export"**
4. Right-click → **Run** to test immediately

---

## To Reconfigure Later

Just run setup again:
```bash
python export_copilot_history.py --setup
```

---

## Troubleshooting

**"Python not found"**  
→ Install from https://www.python.org/downloads/

**"No session files found"**  
→ Did you use Copilot Chat today? Exports only find sessions from today.

**Task Scheduler script failed**  
→ Right-click `schedule_daily.bat` and select "Run as administrator"

---

## That's It!

Your chat history now exports daily to the folder you chose, in both JSON and Markdown formats.

For detailed docs, see `README.md`.
