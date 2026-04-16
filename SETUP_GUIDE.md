# Copilot Chat History Exporter - Complete Setup Guide

A Python automation tool to automatically export VS Code Copilot chat sessions daily to JSON and Markdown formats.

---

## 📋 Prerequisites

Before you start, make sure you have:

### **System Requirements**
- **OS:** Windows 10 or later
- **Python:** 3.7 or higher
- **VS Code:** With Copilot Chat extension installed and used

### **Check Your Python Version**

Open Command Prompt or PowerShell and run:

```bash
python --version
```

If you see `3.7.0` or higher, you're good! If not, [download Python](https://www.python.org/downloads/).

### **Check VS Code Copilot**

1. Open VS Code
2. Look for the **Copilot Chat** icon in the left sidebar (chat bubble icon)
3. If you see it, you're set. If not, install it:
   - Click Extensions (Ctrl+Shift+X)
   - Search for "GitHub Copilot Chat"
   - Click Install

---

## 🚀 Installation & Setup

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/nchandik/copilot-chat-exporter.git
cd copilot-chat-exporter
```

Or download the ZIP file from GitHub and extract it.

### **Step 2: Run Interactive Setup (First Time Only)**

```bash
python export_copilot_history.py --setup
```

You'll be asked 3 questions:

**Question 1: Where to save files?**
```
Default: Documents\Copilot-History
Your choice: [Press Enter to use default OR type your path]
```

Example paths:
- `C:\Users\YourName\Documents\Copilot-History`
- `C:\MyBackup\CopilotChats`
- `D:\Copilot-History`

**Question 2: What time to export daily?**
```
Enter in HH:MM format (24-hour)
Default: 23:00 (11:00 PM)
Your choice: 18:00 (for 6:00 PM)
```

Consider your timezone:
- **IST (India):** 18:00 = 6:00 PM
- **EST (US East):** 18:00 = 6:00 PM  
- **CST (US Central):** 18:00 = 6:00 PM
- **MST (US Mountain):** 18:00 = 6:00 PM
- **PST (US Pacific):** 18:00 = 6:00 PM

**Question 3: What's your timezone?**
```
Choose: IST, EST, CST, MST, or PST
(For reference only, doesn't affect export time)
```

✅ **Your configuration is saved to:** `C:\Users\YourName\.copilot_exporter_config.json`

---

### **Step 3: Test It Works (Important!)**

Run the export once manually to verify it works:

```bash
python export_copilot_history.py
```

You should see:
```
📅 Exporting Copilot chat history for 2026-04-16
📁 Output directory: C:\Users\...\Documents\Copilot-History
🕐 Configured export time: 23:00 (IST)
✅ Found X session file(s)
...
✅ JSON: C:\...\prompt_response_history_2026-04-16.json
✅ Markdown: C:\...\prompt_response_history_2026-04-16.md

🎉 Export complete!
```

Check your output directory — you should see:
- `prompt_response_history_2026-04-16.json` (structured data)
- `prompt_response_history_2026-04-16.md` (readable format)

### **Step 4: Schedule Daily Automation**

#### **Option A: Using Batch File (Easiest)**

1. Right-click `schedule_daily.bat` in the folder
2. Click **"Run as administrator"**
3. The task will be created automatically ✅

#### **Option B: Using PowerShell**

1. Right-click **PowerShell**
2. Click **"Run as Administrator"**
3. Navigate to the folder:
   ```powershell
   cd "C:\path\to\copilot-chat-exporter"
   .\schedule_daily.ps1
   ```

#### **Option C: Manual (Advanced)**

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click **Create Basic Task**
3. **Name:** `Copilot Chat History Export`
4. **Trigger:** Daily at your chosen time
5. **Action:** Start a program
   - **Program:** `C:\path\to\python.exe`
   - **Arguments:** `C:\path\to\export_copilot_history.py`
6. Click **OK**

---

## 📖 How to Use

### **Manual Export (Anytime)**

```bash
python export_copilot_history.py
```

Exports today's chat history using your saved configuration.

### **Export a Specific Past Date**

```bash
python export_copilot_history.py --date 2026-04-15
```

Exports history from April 15, 2026.

### **Export to a Different Directory**

```bash
python export_copilot_history.py --output-dir "C:\Backup\Chats"
```

Temporarily exports to a different location (doesn't change config).

### **Reconfigure Your Settings**

```bash
python export_copilot_history.py --setup
```

Runs setup again to change output directory, time, or timezone.

### **Show Help**

```bash
python export_copilot_history.py --help
```

---

## 📊 Output Format

### **JSON Format** (`prompt_response_history_2026-04-16.json`)

Structured data with metadata:

```json
{
  "date": "2026-04-16",
  "sessionFilesCount": 4,
  "historyCount": 131,
  "history": [
    {
      "role": "user",
      "message": "your prompt",
      "sourceSession": "session-id",
      "source": "kind0.requests.message",
      "timestamp": 1776340394311
    },
    {
      "role": "assistant",
      "message": "assistant response",
      "sourceSession": "session-id",
      "source": "kind0.requests.response"
    }
  ]
}
```

Use for: Parsing, analysis, integrations, APIs

### **Markdown Format** (`prompt_response_history_2026-04-16.md`)

Human-readable format:

```markdown
# Prompt & Response History - 2026-04-16

### Entry 1 — USER

your prompt here

---

### Entry 2 — ASSISTANT

assistant response here

---
```

Use for: Reading, sharing, documentation

---

## 🔧 Configuration File

**Location:** `C:\Users\YourName\.copilot_exporter_config.json`

**Example:**
```json
{
  "output_dir": "C:\\Users\\Satish\\Documents\\Copilot-History",
  "export_time": "18:00",
  "timezone": "IST",
  "created_at": "2026-04-16T19:31:52.303648",
  "version": "1.0"
}
```

**Edit manually if needed:**
- Change `output_dir` to move exports to a different location
- Change `export_time` to run at a different time (HH:MM format)
- Change `timezone` for documentation (doesn't affect actual export time)

---

## ⚠️ Limitations

### **1. Chat History Availability**
- Only exports chats from **today's date** (or specified date)
- Sessions must have been modified on that date
- If you haven't used Copilot Chat on a day, no file will be created

### **2. File Locations**
- Only finds chats in the default VS Code location:
  ```
  C:\Users\YourName\AppData\Roaming\Code\User\workspaceStorage
  ```
- If you've moved VS Code or use portable versions, it may not find the files

### **3. Time Format**
- Export time must be in 24-hour format (HH:MM)
- No automatic timezone conversion
- All times are local machine time

### **4. Chat Content**
- Extracts text content only
- Does not export code blocks with full formatting
- Does not export images or file attachments from chats
- Best-effort extraction — some formatting may be lost

### **5. Scheduled Task**
- Scheduled task runs at the exact time you set
- Your computer must be running at that time
- If your computer is off or sleeping, the export won't run
- You can always run manually: `python export_copilot_history.py`

### **6. File Size**
- If you have many chat sessions, the JSON/MD files can be large (50+ KB)
- No automatic cleanup of old exports

### **7. Multiple Workspaces**
- If you use multiple VS Code workspaces, all chats are consolidated into one export

---

## 🔍 Troubleshooting

### **"Python not found"**

```
Error: 'python' is not recognized as an internal or external command
```

**Solution:**
- Install Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal after installing

### **"No session files found"**

```
❌ Error finding session files: ...
```

**Causes & Solutions:**
1. **Didn't use Copilot Chat today** → Chat a bit and try again
2. **Using different VS Code setup** → Check `AppData\Roaming\Code\User\workspaceStorage` exists
3. **First-time setup failed** → Run `python export_copilot_history.py --setup` again

### **"Config file not found"**

```
🔧 First time setup required...
```

**Solution:** This is normal! Run setup:
```bash
python export_copilot_history.py --setup
```

### **"Permission denied" on Windows**

```
Access is denied
```

**Solutions:**
- Run terminal as **Administrator** (right-click → Run as Administrator)
- Check your output directory is writable
- Make sure antivirus isn't blocking Python

### **Scheduled task not running**

**Causes & Solutions:**
1. **Computer was off at scheduled time**
   - Keep computer on or set a different time
2. **Task Scheduler error**
   - Right-click the task in Task Scheduler → Run to test
3. **Python path wrong in task**
   - Delete the task and run `schedule_daily.bat` again

To verify the task:
1. Press `Win + R`, type `taskschd.msc`
2. Look for "Copilot Chat History Export"
3. Right-click → Properties to see the command

### **Output files empty or incomplete**

**Solution:** 
- Make sure VS Code Copilot Chat was actively used
- Check the generated files have content: `dir /s C:\Users\YourName\.copilot_exporter_config.json`

---

## 💡 Tips & Best Practices

### **1. Regular Backups**
The exported files are your only backup of chat history. Consider:
- Setting export directory to a cloud folder (OneDrive, Google Drive)
- Manually backing up the directory weekly

### **2. Export Time**
Choose a time when your computer is usually on:
- **Best:** Evening time (18:00, 20:00)
- **Avoid:** Very late night when you shut down
- **Note:** If you work 24/7, any time is fine

### **3. Multiple Teams**
If your team members use this:
- Each person runs setup with their own config
- Share the GitHub repo link
- Each person has their own exports in their Documents folder

### **4. Exporting to Cloud**
For cloud backup, set output directory to:
- `C:\Users\YourName\OneDrive\Documents\Copilot-History`
- `C:\Users\YourName\Google Drive\Copilot-History`
- `C:\Users\YourName\Dropbox\Copilot-History`

### **5. Archiving Old Files**
After a month, you may have many export files. You can:
- Zip older files: `tar -czf history_april.tar.gz *.json`
- Move to archive folder: `mkdir archive && mv *.md archive\`

---

## 🔐 Privacy & Security

### **What Gets Exported?**
- All text from your Copilot Chat conversations
- Timestamps and session IDs
- **Does NOT include:**
  - Your passwords or secrets (hopefully you don't paste those!)
  - IDE or extension data
  - System information

### **Where Files Are Stored**
- Your output directory (you choose)
- Default: `Documents\Copilot-History`
- Fully under your control

### **Data Safety**
- Files are JSON/Markdown plain text
- Can be read by any text editor
- Consider encrypting if storing sensitive conversations

---

## 📞 Support

**Having issues?**
1. Check this guide's **Troubleshooting** section
2. Run `python export_copilot_history.py --help`
3. Check [GitHub Issues](https://github.com/nchandik/copilot-chat-exporter/issues)

**Want to contribute?**
- Submit pull requests or issues on GitHub
- Suggest features or improvements

---

## 📄 License

Feel free to use, modify, and share this tool with your team.

---

**Happy exporting!** 🚀
