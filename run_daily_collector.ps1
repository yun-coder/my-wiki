# MyWiki Daily Collector Wrapper
# Uses system Python at D:\学习院\my-wiki to run daily collection
$exe = "C:\Users\panda\AppData\Local\Programs\Python\Python311\python.exe"
$script = "D:\学习院\my-wiki\scripts\daily_collector.py"
$output = & $exe $script 2>&1
$exitCode = $LASTEXITCODE
if ($output) { $output | Out-String | Write-Host }
exit $exitCode
