# Copilot Chat History Exporter Setup Guide

This guide covers installation, first-time setup, scheduling, and verification.

## Prerequisites

- Windows 10 or later
- Python 3.7 or later
- VS Code with Copilot Chat used at least once

Check Python:

```bash
python --version
```

## Install And Configure

### 1. Get the repository

```bash
git clone https://github.com/nchandik/copilot-chat-exporter.git
cd copilot-chat-exporter
```

If you are working from `nchandik/copilot-chat-exporter`, do not push personal changes directly to `main`. Use a fork or separate branch.

### 2. Run setup

```bash
python export_copilot_history.py --setup
```

Setup prompts:

1. Output directory
2. Default run mode: automatic or manual
3. Daily export time if automatic mode is selected
4. Timezone for reference

Example output directory values:

- `C:\Users\YourName\Documents\Copilot-History`
- `C:\MyBackup\CopilotChats`
- `D:\Copilot-History`

Configuration is saved to `C:\Users\YourName\.copilot_exporter_config.json`.

Example config:

```json
{
  "output_dir": "C:\\Users\\YourName\\Documents\\Copilot-History",
  "run_mode": "automatic",
  "export_time": "20:00",
  "timezone": "IST",
  "created_at": "2026-04-20T17:30:00.000000",
  "version": "1.0"
}
```

Notes:

- `run_mode` is the default behavior.
- `export_time` matters only for automatic mode.
- The Task Scheduler trigger is the source of truth for the actual automatic run time.

### 3. Verify one manual run

```bash
python export_copilot_history.py --interactive
```

Confirm both files are created in your output directory:

- `chat_history_YYYY-MM-DD.json`
- `chat_history_YYYY-MM-DD.md`

## Set Up Automatic Export

Automatic export runs through Windows Task Scheduler.

Important:

- The exporter itself does not require Administrator rights.
- Some helper scripts may ask for Administrator rights depending on local Windows policy or how they are launched.
- If a helper script fails because of elevation, create the task manually or with a user-level `schtasks` command.

### Option A: `schedule_daily.bat`

1. Run `schedule_daily.bat`
2. If it works, the task is created
3. If it says it must be run as Administrator, rerun it elevated or use Option C

### Option B: `schedule_daily.ps1`

1. Open PowerShell in the repository folder
2. Run:

```powershell
.\schedule_daily.ps1
```

3. If the script asks for elevation, rerun PowerShell as Administrator or use Option C

### Option C: manual Task Scheduler setup

1. Open Task Scheduler
2. Create a basic task named `Copilot Chat History Export`
3. Set a daily trigger at your preferred time
4. Set the action to start your Python executable
5. Pass the script path plus `--scheduled` as the arguments

Example:

- Program: `C:\path\to\python.exe`
- Arguments: `C:\path\to\export_copilot_history.py --scheduled`

### Validate the scheduled task

1. Open Task Scheduler
2. Find `Copilot Chat History Export`
3. Use Run once to test it
4. Confirm `Last Run Result` is `0`
5. Confirm the expected JSON and Markdown files exist

## Daily Usage

Manual export with saved defaults:

```bash
python export_copilot_history.py
```

Specific past date:

```bash
python export_copilot_history.py --date 2026-04-15
```

Different output directory for one run:

```bash
python export_copilot_history.py --output-dir "C:\Backup\Chats"
```

Force manual mode:

```bash
python export_copilot_history.py --interactive
```

Force scheduled mode:

```bash
python export_copilot_history.py --scheduled
```

## What To Expect

- Automatic mode is non-interactive
- Automatic mode overwrites that date's existing output files
- The task can run while VS Code is closed
- The machine must be on and not asleep unless task settings say otherwise
- Running while signed out depends on the task's logon settings

## Troubleshooting

`python` is not recognized

- Install Python
- Add Python to PATH during installation
- Restart the terminal

`First time setup required`

Run:

```bash
python export_copilot_history.py --setup
```

`No session files found`

- Make sure Copilot Chat was used for that date
- Confirm VS Code data exists under `%APPDATA%\Code\User\workspaceStorage`

`Access is denied`

- Check whether the output directory is writable
- Check whether antivirus or endpoint protection is blocking the process
- Use Administrator only if the specific scheduling helper requires it

Scheduled task does not run

- Run the task once manually from Task Scheduler
- Verify the Python path and script arguments
- Check whether the machine was off or asleep

Output files are empty or missing

- Make sure there was chat activity for the selected date
- Verify the output directory in the config file

## Privacy

- Exported files can contain sensitive prompts and responses
- Store them in a secure directory
- Apply your normal data handling policy before sharing them

## Support

1. Run `python export_copilot_history.py --help`
2. Check `FAQ.md`
3. Check GitHub issues for the repository
