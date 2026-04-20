# Copilot Chat History Exporter

Export VS Code Copilot chat sessions to JSON and Markdown on demand or on a daily schedule.

## Features

- Interactive first-run setup
- Automatic or manual run modes
- JSON and Markdown output for each export date
- No third-party Python packages required
- Windows Task Scheduler support for daily automation

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/nchandik/copilot-chat-exporter.git
cd copilot-chat-exporter
```

### 2. Run first-time setup

```bash
python export_copilot_history.py --setup
```

Setup asks for:
- Output directory
- Default run mode: `automatic` or `manual`
- Daily export time for automatic mode
- Timezone for reference

Configuration is saved to `~\.copilot_exporter_config.json`.

### 3. Test one export

```bash
python export_copilot_history.py
```

### 4. Optional: schedule automatic export

Automatic export is driven by Windows Task Scheduler, not by VS Code.

Option A: helper script

1. Run `schedule_daily.bat`
2. If Windows blocks it or the script asks for elevation, rerun it as Administrator

Option B: PowerShell helper

1. Open PowerShell in this folder
2. Run `./schedule_daily.ps1`
3. If the script asks for elevation, rerun PowerShell as Administrator

Option C: create the task manually

1. Open Task Scheduler
2. Create a daily task named `Copilot Chat History Export`
3. Set the trigger to your preferred time
4. Set the action to start `python.exe`
5. Pass `export_copilot_history.py --scheduled` as the program arguments

Important:
- You do not need Administrator rights to run the exporter itself.
- Some scheduling helper flows may require Administrator rights depending on local policy or how the helper script is launched.
- A user-level scheduled task can still work without Administrator rights.

## Usage

```bash
# Run setup
python export_copilot_history.py --setup

# Export using saved config
python export_copilot_history.py

# Export a specific date
python export_copilot_history.py --date 2026-04-15

# Override output directory
python export_copilot_history.py --output-dir "C:\My\Output\Path"

# Force manual interactive mode
python export_copilot_history.py --interactive

# Force scheduled non-interactive mode
python export_copilot_history.py --scheduled

# Show help
python export_copilot_history.py --help
```

Manual mode supports exporting previous dates through the interactive prompt or by passing `--date`.

## Configuration

Configuration file: `~\.copilot_exporter_config.json`

Example:

```json
{
  "output_dir": "C:\\Users\\YourUsername\\Documents\\Copilot-History",
  "run_mode": "automatic",
  "export_time": "20:00",
  "timezone": "IST",
  "created_at": "2026-04-20T17:30:00.000000",
  "version": "1.0"
}
```

Notes:
- `run_mode` controls the default behavior.
- `export_time` matters only for automatic mode.
- The actual automatic run time is controlled by the Task Scheduler trigger.

## Output

The exporter writes one file pair per date:

- `chat_history_YYYY-MM-DD.json`
- `chat_history_YYYY-MM-DD.md`

JSON contains structured data. Markdown contains a readable transcript.

## First-Run Validation

1. Run `python export_copilot_history.py --setup`
2. Confirm `run_mode` in `~\.copilot_exporter_config.json`
3. Run `python export_copilot_history.py --interactive`
4. Confirm both output files were created
5. If using automatic mode, run the scheduled task once and confirm it succeeds

## Troubleshooting

`First time setup required`

Run:

```bash
python export_copilot_history.py --setup
```

`No session files found`

- Make sure Copilot Chat was used for the target date
- Confirm VS Code session data exists under `%APPDATA%\Code\User\workspaceStorage`

`Permission denied`

- Check that the output directory is writable
- Try an absolute output path
- Use Administrator only if the specific scheduling helper requires it

`Scheduled task does not run`

- Run the task manually once from Task Scheduler
- Verify the Python path and script arguments in the task
- Check whether the machine was asleep or signed out when the task was due to run

## Sharing With Colleagues

Team members can clone the repository and run their own setup locally.

- Do not push personal changes directly to `main` in `nchandik/copilot-chat-exporter`
- Use a fork or a separate branch for changes
- Each user gets a local config file and local scheduled task

## Requirements

- Windows 10 or later
- Python 3.7+
- VS Code with Copilot Chat

## More Detail

See `SETUP_GUIDE.md` for the full setup flow and `FAQ.md` for behavior questions.
