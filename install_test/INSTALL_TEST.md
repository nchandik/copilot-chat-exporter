# Installation & Testing Guide

## Environment
- Python: 3.14.2 ✅
- OS: Windows 10+
- VS Code: Required with Copilot Chat extension
- Date: 2026-04-16

## Test Scenarios

### Scenario 1: Run Setup (First Time)
```bash
python ../export_copilot_history.py --setup
```
Expected: Interactive prompts for output directory, export time, timezone

### Scenario 2: Export Today's Chat
```bash
python ../export_copilot_history.py --days-ago 0 --output-dir ./exports
```
Expected: JSON + Markdown files for today

### Scenario 3: Export Yesterday
```bash
python ../export_copilot_history.py --days-ago 1 --output-dir ./exports
```
Expected: JSON + Markdown files for yesterday

### Scenario 4: Batch Export (Last 3 Days)
```bash
python ../export_copilot_history.py --batch 3 --output-dir ./exports
```
Expected: 3 days worth of exports

### Scenario 5: Custom Date
```bash
python ../export_copilot_history.py --date 2026-04-14 --output-dir ./exports
```
Expected: Specific date export

## Validation Checklist
- [ ] Setup completes without errors
- [ ] Config file created at ~/.copilot_exporter_config.json
- [ ] Exports create JSON files
- [ ] Exports create Markdown files
- [ ] File sizes > 0 bytes
- [ ] JSON is valid (can be parsed)
- [ ] Markdown is readable
- [ ] No error messages for valid dates
- [ ] Error handling works for invalid inputs

