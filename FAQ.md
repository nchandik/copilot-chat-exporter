# Copilot Chat History Exporter FAQ

## Can I use both automatic and manual export?

Yes. `run_mode` sets the default behavior, but you can still use either mode when needed.

- Use `python export_copilot_history.py --scheduled` for automatic non-interactive behavior.
- Use `python export_copilot_history.py --interactive` for manual interactive behavior.

## If I manually export at 2 PM and automatic export runs at 8 PM, what happens?

The 8 PM automatic run exports the same date again and overwrites that day's files. The final file for the day reflects the latest export run.

## Will automatic export still run if VS Code is closed?

Yes. Automatic export is run by Windows Task Scheduler, not by VS Code. It reads chat session files already saved on disk.

## What if there are no chats for that day?

The task still runs, but it may produce no entries or no useful export content for that date.

## Does setup choice lock me into one mode forever?

No. Setup chooses the default mode. You can still override it later with `--interactive` or `--scheduled`.

## Why is there a question about automatic vs manual mode during setup?

Because scheduled jobs must run without stopping for prompts, while manual runs can safely ask questions like which date to export or whether to overwrite files.

## What controls the actual automatic run time?

Windows Task Scheduler controls the actual automatic run time. The exporter config stores your preferred mode and related settings.

## What date format should I use for manual or custom date export?

The exporter accepts these common input formats and normalizes them internally to YYYY-MM-DD:

- YYYY-MM-DD (example: 2026-04-17)
- YYYY/MM/DD (example: 2026/04/17)
- MM/DD/YYYY (example: 04/17/2026)
- Month name forms (example: April 17, 2026 or Apr 17, 2026)

## Why does 17-04-2026 show as invalid?

17-04-2026 is DD-MM-YYYY format, which is not currently in the accepted set. This is intentional to avoid ambiguity across regions.

## Do I get multiple files for the same day?

No, not by default. The exporter uses one JSON file and one Markdown file per day, so later runs for the same day replace earlier ones.

## Should users push their own changes to this repository's main branch?

No. Users should clone `nchandik/copilot-chat-exporter` to use the exporter, but they should not push changes directly to `main`.

- If they need personal changes, they should use their own fork.
- If they are collaborating on enhancements, they should work in a separate branch and follow the normal review process.
