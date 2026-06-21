$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $root ".runtime"
New-Item -ItemType Directory -Force -Path $runtime | Out-Null

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    Write-Error "Missing virtual environment. Run setup from README.md first."
    exit 1
}

function Quote-Arg([string] $value) {
    '"' + ($value -replace '"', '\"') + '"'
}

function Start-ManagedProcess([string] $name, [string[]] $arguments) {
    $command = (Quote-Arg $python) + " " + (($arguments | ForEach-Object { Quote-Arg $_ }) -join " ")
    $result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine = $command
        CurrentDirectory = $root
    }
    if ($result.ReturnValue -ne 0) {
        Write-Error "Failed to start $name. Win32_Process.Create returned $($result.ReturnValue)."
        exit 1
    }
    Set-Content -Encoding ascii -LiteralPath (Join-Path $runtime "$name.pid") -Value $result.ProcessId
    return $result.ProcessId
}

$envArgs = @()
if ($env:SGPOOLS_ENV_FILE) {
    $envArgs = @("--env-file", $env:SGPOOLS_ENV_FILE)
}

$interval = if ($env:SGPOOLS_SCRAPE_INTERVAL_MINUTES) { $env:SGPOOLS_SCRAPE_INTERVAL_MINUTES } else { "60" }
$dashboardPort = if ($env:SGPOOLS_DASHBOARD_PORT) { $env:SGPOOLS_DASHBOARD_PORT } else { "8765" }

Write-Output "Starting Singapore Pools odds scraper loop every $interval minutes..."
$scraperArgs = @("-m", "sgpools_trend.cli") + $envArgs + @("scrape-loop", "--interval-minutes", $interval)
$scraperPid = Start-ManagedProcess "scraper" $scraperArgs

Write-Output "Starting dashboard on http://127.0.0.1:$dashboardPort ..."
$dashboardArgs = @("-m", "sgpools_trend.dashboard") + $envArgs + @("--port", $dashboardPort)
$dashboardPid = Start-ManagedProcess "dashboard" $dashboardArgs

if (-not $env:SGPOOLS_ENV_FILE -and -not $env:TELEGRAM_BOT_TOKEN) {
    Write-Output "TELEGRAM_BOT_TOKEN or SGPOOLS_ENV_FILE is not set. Skipping Telegram bot."
    Write-Output "Started scraper PID $scraperPid and dashboard PID $dashboardPid."
    exit 0
}

Write-Output "Starting Telegram bot..."
$botArgs = @("-m", "sgpools_trend.bot") + $envArgs
$botPid = Start-ManagedProcess "bot" $botArgs

Write-Output "Started."
Write-Output "Scraper PID: $scraperPid"
Write-Output "Dashboard PID: $dashboardPid"
Write-Output "Bot PID: $botPid"
