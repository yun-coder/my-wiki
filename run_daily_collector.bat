@echo off
REM MyWiki Daily Collector Wrapper

cd /d D:\ѧϰԺ\my-wiki

set LOG_DIR=D:\ѧϰԺ\my-wiki\state\daily\logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f "tokens=1-3 delims=/- " %%a in ('echo %DATE%') do set TD=%%a%%b%%c
for /f "tokens=1-3 delims=:." %%a in ('echo %TIME%') do set TT=%%a%%b%%c
set TT=%TT: =0%
set LOG_FILE=%LOG_DIR%\collect_%TD%_%TT%.log

echo [%DATE% %TIME%] Starting daily collector... >> "%LOG_FILE%" 2>&1

C:\Users\panda\AppData\Local\Programs\Python\Python311\python.exe scripts\daily_collector.py >> "%LOG_FILE%" 2>&1

set EXIT_CODE=%ERRORLEVEL%
echo [%DATE% %TIME%] Finished with exit code %EXIT_CODE% >> "%LOG_FILE%" 2>&1

exit /b %EXIT_CODE%