# Quick Start Guide (5 Minutes)

For colleagues who want to get started immediately.

---

## ✅ Prerequisites Check

Before starting, verify you have:
- **Windows 10+**
- **Python 3.7+** (run: `python --version`)
- **VS Code with Copilot Chat** (visible in left sidebar)
- **Git** (to clone the repo)

**Using Copilot Chat for help?** Copy any prompt from the **[COPILOT_PROMPTS.md](COPILOT_PROMPTS.md)** file for step-by-step interactive guidance.

---

## 🚀 3-Step Setup

### Step 1: Clone & Interactive Configuration

```bash
git clone https://github.com/nchandik/copilot-chat-exporter.git
cd copilot-chat-exporter
python export_copilot_history.py --setup
```

You'll be asked:
1. **Where to save files?** → Press Enter for default or choose a path
2. **What time to export?** → Enter `18:00` (6:00 PM) or your preferred time
3. **Your timezone?** → Choose: IST, EST, CST, MST, or PST

✅ Config saved to: `C:\Users\YourUsername\.copilot_exporter_config.json`

### Step 2: Test It Works

```bash
python export_copilot_history.py
```

Check for success:
```
✅ JSON: C:\...\prompt_response_history_2026-04-16.json
✅ Markdown: C:\...\prompt_response_history_2026-04-16.md
🎉 Export complete!
```

### Step 3: Schedule Daily Automation

**Easiest — Right-click as Admin:**
```bash
schedule_daily.bat
```

**Alternative — PowerShell:**
```powershell
.\schedule_daily.ps1
```

Done! Exports run automatically at your chosen time.

---

## ✨ That's It!

Your chat history now exports daily in both JSON (structured) and Markdown (readable) formats.

---

## 🎯 Common Next Steps

**Verify scheduling works:**
1. Press `Win + R`
2. Type `taskschd.msc`
3. Look for **"Copilot Chat History Export"**
4. Right-click → **Run** to test

**Reconfigure later:**
```bash
python export_copilot_history.py --setup
```

**Export a past date:**
```bash
python export_copilot_history.py --date 2026-04-15
```

---

## ❓ Need Help?

- **Prefer interactive guidance?** Copy prompts from [COPILOT_PROMPTS.md](COPILOT_PROMPTS.md) and paste into Copilot Chat
- **Troubleshooting?** See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Full documentation?** See [README.md](README.md)
