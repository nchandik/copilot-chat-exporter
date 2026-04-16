# Copilot Chat History Exporter - Windows Task Scheduler Setup (PowerShell)
#
# This PowerShell script creates a scheduled task to export Copilot chat history daily.
#
# NOTE: Run "python export_copilot_history.py --setup" first to configure preferences!
#
# BEFORE RUNNING:
#   1. Run PowerShell as Administrator (right-click → Run as Administrator)
#   2. Execute: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser (if needed)
#   3. Then: .\schedule_daily.ps1

# ====== CONFIGURATION ======
# These are only used if config file doesn't exist yet.
# For first time: Run "python export_copilot_history.py --setup" to configure interactively

# Full path to python.exe (leave empty to auto-detect)
$PythonPath = ""

# Full path to this script's directory (where export_copilot_history.py is located)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Task name in Task Scheduler
$TaskName = "Copilot Chat History Export"

# ====== END CONFIGURATION ======

Write-Host ""
Write-Host "========================================"
Write-Host "Copilot Chat History - Task Scheduler Setup"
Write-Host "========================================"
Write-Host ""

# Check for admin privileges
$IsAdmin = [Security.Principal.WindowsIdentity]::GetCurrent().Groups -match "S-1-5-32-544"
if (-not $IsAdmin) {
    Write-Host "ERROR: This script must be run as Administrator." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'"
    Read-Host "Press Enter to exit"
    exit 1
}

# Auto-detect Python if not specified
if ([string]::IsNullOrEmpty($PythonPath)) {
    $PythonPath = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
    if ($null -eq $PythonPath) {
        Write-Host "ERROR: Python not found. Install Python or set PythonPath manually." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check if script exists
$ScriptPath = Join-Path $ScriptDir "export_copilot_history.py"
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: export_copilot_history.py not found in:" -ForegroundColor Red
    Write-Host "  $ScriptDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Configuration:"
Write-Host "  Python: $PythonPath"
Write-Host "  Script: $ScriptPath"
Write-Host ""
Write-Host "NOTE: Output directory and export time are read from:"
Write-Host "  $ENV:USERPROFILE\.copilot_exporter_config.json"
Write-Host ""
Write-Host "If this is your first time, run:"
Write-Host "  python `"$ScriptPath`" --setup"
Write-Host ""

# Create scheduled task
Write-Host "Creating scheduled task..." -ForegroundColor Cyan

$Arguments = "`"$ScriptPath`""
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $Arguments

$Trigger = New-ScheduledTaskTrigger -Daily -At "23:00"

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RunWithoutNetwork

try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Force | Out-Null

    Write-Host ""
    Write-Host "SUCCESS: Task created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task name: $TaskName"
    Write-Host "  Default time: 23:00 (can be customized via config)"
    Write-Host "  Command: `"$PythonPath`" `"$Arguments`""
    Write-Host ""
    Write-Host "To customize the export time:"
    Write-Host "  1. Open Task Scheduler (tasksched.msc)"
    Write-Host "  2. Find 'Copilot Chat History Export'"
    Write-Host "  3. Right-click and select 'Properties' to edit the schedule"
    Write-Host "  4. Or run 'python `"$ScriptPath`" --setup' to reconfigure"
    Write-Host ""
    Write-Host "To verify the task was created:"
    Write-Host "  1. Open Task Scheduler (tasksched.msc)"
    Write-Host "  2. Look for '$TaskName' in the task list"
    Write-Host "  3. Right-click and select 'Run' to test it immediately"
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to create task:" -ForegroundColor Red
    Write-Host "  $_" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
