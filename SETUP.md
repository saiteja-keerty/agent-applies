# Job Hunter Automation System

## What It Does
Automatically scrapes remote job listings, stores them in Excel, and sends personalized emails with your resume to all jobs. Prevents duplicate emails and tracks all activity.

## Files Required
- `job_hunter.py` - Scrapes jobs from APIs
- `send_emails.py` - Sends emails and prevents duplicates
- `full_job_cycle.bat` - Runs both scraping + sending daily
- `job_applications.xlsx` - Excel database of jobs
- `sent_emails.json` - Duplicate prevention tracker
- `Saiteja_keerty_Resume.pdf` - Your resume

## Daily Automation
Runs automatically every day at **1:11 PM CST**

### What Happens:
1. Scrapes latest jobs from Remotive, Arbeitnow, Jobicy APIs
2. Saves new jobs to Excel
3. Sends emails to ALL jobs (not previously sent)
4. Marks jobs as "Sent" in Excel
5. Stores sent emails in JSON to prevent duplicates

### Laptop Status:
- **ON**: Runs normally at 1:11 PM
- **SLEEPING**: Wakes automatically and runs
- **OFF**: Won't run (power down = no wake)

### If You Open Laptop Late:
- Task runs as soon as you log in after scheduled time
- No emails missed

## How to Run Manually

```bash
# Scrape jobs only
python job_hunter.py

# Send emails only
echo yes | python send_emails.py

# Do both at once
.\full_job_cycle.bat
```

## Duplicate Prevention
- `sent_emails.json` tracks every email sent
- Never sends same email twice
- Tries email_1, then email_2, then email_3 until one succeeds
- Only successful sends are recorded

## Excel Status
- Status column shows "Sent" after email delivery
- Timestamp recorded in sent_emails.json
- Complete audit trail maintained

## Email Configuration
- **From**: saiteja.keerty@gmail.com
- **To**: 3 email addresses per company (auto-tries all)
- **Attachment**: Your resume PDF
- **Template**: Professional cover letter

## Stop/Modify Schedule
1. Open Task Scheduler (`taskschd.msc`)
2. Find "JobHunterEmailSender"
3. Edit as needed

## Manual Testing
```bash
python send_emails.py
# Set DRY_RUN = True in send_emails.py to preview emails
```

---
**System Status**: ✅ Production Ready
**Jobs Scraped**: 13
**Emails Sent**: 26 (13 jobs × 2 emails each)
**Next Run**: Tomorrow at 1:11 PM
