@echo off
REM Batch file to run email sender automatically
REM This is designed to be called by Windows Task Scheduler

REM Set UTF-8 encoding to handle Unicode characters
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo ========================================
echo  AUTOMATED EMAIL SENDER
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Log the start time
echo [%DATE% %TIME%] Starting automated email sending >> email_scheduler.log

REM Run the Python script with automatic confirmation
echo yes | python send_emails.py >> email_scheduler.log 2>&1

REM Log completion
echo [%DATE% %TIME%] Email sending completed >> email_scheduler.log

echo.
echo ========================================
echo  AUTOMATED EMAIL SENDING COMPLETE
echo ========================================
echo Check email_scheduler.log for details
echo.