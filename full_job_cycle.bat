@echo off
REM Combined script: Scrape jobs + Send emails
REM This runs both job_hunter.py and send_emails.py back-to-back

echo ========================================
echo  🤖 FULL JOB HUNTING CYCLE
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Set UTF-8 encoding
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo [%DATE% %TIME%] Starting full job hunting cycle >> full_cycle.log

echo.
echo ========================================
echo  📊 PHASE 1: SCRAPING NEW JOBS
echo ========================================
echo.

REM Run job scraping
echo [%DATE% %TIME%] Starting job scraping >> full_cycle.log
python job_hunter.py >> full_cycle.log 2>&1
echo [%DATE% %TIME%] Job scraping completed >> full_cycle.log

echo.
echo ========================================
echo  📧 PHASE 2: SENDING EMAILS
echo ========================================
echo.

REM Wait a moment
timeout /t 5 /nobreak >nul

REM Run email sending
echo [%DATE% %TIME%] Starting email sending >> full_cycle.log
echo yes | python send_emails.py >> full_cycle.log 2>&1
echo [%DATE% %TIME%] Email sending completed >> full_cycle.log

echo.
echo ========================================
echo  ✅ FULL CYCLE COMPLETE
echo ========================================
echo.
echo 📊 Jobs scraped and saved to Excel
echo 📧 Emails sent to new applications
echo 📝 Check full_cycle.log for details
echo.

REM Log completion
echo [%DATE% %TIME%] Full job hunting cycle completed >> full_cycle.log