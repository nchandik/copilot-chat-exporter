#!/bin/bash

echo "=========================================="
echo "TEST SCENARIO 1: --days-ago 1 (yesterday)"
echo "=========================================="
python export_copilot_history.py --days-ago 1 --output-dir ./test_output 2>&1 | grep -E "(Exporting|Found|entries|JSON|Markdown|ERROR|WARN)"
echo ""

echo "=========================================="
echo "TEST SCENARIO 2: --batch 2 (last 2 days)"
echo "=========================================="
python export_copilot_history.py --batch 2 --output-dir ./test_output 2>&1 | grep -E "(Exporting|Found|entries|JSON|Markdown|ERROR|No session|Export complete)"
echo ""

echo "=========================================="
echo "TEST SCENARIO 3: --date with past date"
echo "=========================================="
python export_copilot_history.py --date 2026-04-14 --output-dir ./test_output 2>&1 | grep -E "(Exporting|Found|entries|ERROR|No session)"
echo ""

echo "=========================================="
echo "TEST SCENARIO 4: Error case - negative days"
echo "=========================================="
python export_copilot_history.py --days-ago -1 --output-dir ./test_output 2>&1 | grep "ERROR"
echo ""

echo "=========================================="
echo "TEST SCENARIO 5: Error case - future date"
echo "=========================================="
python export_copilot_history.py --date 2099-12-31 --output-dir ./test_output 2>&1 | grep "future"
echo ""

echo "=========================================="
echo "TEST SCENARIO 6: Verify files were created"
echo "=========================================="
ls -lh test_output/prompt_response_history_*.json 2>/dev/null | wc -l
echo "JSON files created"
ls -lh test_output/prompt_response_history_*.md 2>/dev/null | wc -l
echo "Markdown files created"
