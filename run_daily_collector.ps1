# MyWiki Daily Collector Wrapper
# Uses the project directory containing this wrapper to run daily collection
$exe = "C:\Users\panda\AppData\Local\Programs\Python\Python311\python.exe"
$script = Join-Path $PSScriptRoot "scripts\daily_collector.py"
$output = & $exe $script 2>&1
$exitCode = $LASTEXITCODE
if ($output) { $output | Out-String | Write-Host }
exit $exitCode
