@echo off
setlocal
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $ErrorActionPreference = 'SilentlyContinue'; foreach ($name in @('scraper','bot')) { $pidFile = Join-Path '%CD%' \".runtime\$name.pid\"; if (Test-Path -LiteralPath $pidFile) { $raw = (Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1); $pidValue = 0; if ([int]::TryParse($raw, [ref]$pidValue)) { $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue; if ($proc) { Stop-Process -Id $pidValue -Force; Write-Output \"Stopped $name PID $pidValue\" } else { Write-Output \"$name PID $pidValue is not running\" } } else { Write-Output \"Invalid $name PID file\" }; Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue } else { Write-Output \"No $name PID file\" } } }"
