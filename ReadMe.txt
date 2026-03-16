╔══════════════════════════════════════════════════╗
║        FREE JOB HUNTER — SETUP GUIDE            ║
╚══════════════════════════════════════════════════╝

REQUIREMENTS: Python 3.9+  |  8GB RAM fine  |  Cost: $0

──────────────────────────────────────────────────
 STEP 1: Install Python (if you don't have it)
──────────────────────────────────────────────────
  Download from: https://python.org/downloads
  (Tick "Add Python to PATH" on Windows)

──────────────────────────────────────────────────
 STEP 2: Install dependencies
──────────────────────────────────────────────────
  Open terminal / command prompt and run:

    pip install requests beautifulsoup4 openpyxl groq

  That's it — only ~50MB total, no heavy models needed.

──────────────────────────────────────────────────
 STEP 3: Get your FREE Groq API key (for AI)
──────────────────────────────────────────────────
  1. Go to: https://console.groq.com
  2. Sign up (free, no credit card)
  3. Click "API Keys" → "Create API Key"
  4. Copy the key

  In job_hunter.py, replace:
    GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
  with your actual key.

  Why Groq? It runs Llama 3 (open source AI) for FREE
  and is very fast. No local GPU needed — it runs in
  their cloud.

──────────────────────────────────────────────────
 STEP 4: Edit your info in job_hunter.py
──────────────────────────────────────────────────
  Open job_hunter.py in any text editor and fill in:

    YOUR_NAME       = "Your Full Name"
    YOUR_EMAIL      = "you@email.com"
    YOUR_PHONE      = "+1 555-000-0000"
    JOB_TITLES      = ["your job title", "alternate title"]
    LOCATION        = "Remote"   # or "New York" etc.
    RESUME_TEXT     = """paste your resume here"""

──────────────────────────────────────────────────
 STEP 5: Run it
──────────────────────────────────────────────────
  In terminal:
    python job_hunter.py

  Wait 2-5 minutes. It will create:
    job_applications.xlsx  ← your results!

──────────────────────────────────────────────────
 STEP 6: Run it automatically every night
──────────────────────────────────────────────────

  WINDOWS (Task Scheduler):
  - Search "Task Scheduler" → Create Basic Task
  - Trigger: Daily at 2:00 AM
  - Action: Start a Program → python.exe
  - Arguments: C:\path\to\job_hunter.py

  MAC / LINUX (cron):
  - Open terminal: crontab -e
  - Add this line (runs at 2am daily):
    0 2 * * * /usr/bin/python3 /path/to/job_hunter.py

──────────────────────────────────────────────────
 WHAT THE EXCEL FILE CONTAINS
──────────────────────────────────────────────────
  Column A:  Status (To Apply / Applied / Interviewing)
  Column B:  Company name
  Column C:  Job title
  Column D:  Location
  Column E:  Source website
  Column F:  Direct apply URL (click to open)
  Column G:  Guessed email 1 (e.g. careers@company.com)
  Column H:  Guessed email 2
  Column I:  Guessed email 3
  Column J:  AI-written cover letter (copy into email)
  Column K:  Date found
  Column L:  Your notes

──────────────────────────────────────────────────
 FREE JOB SOURCES USED
──────────────────────────────────────────────────
  • Remotive.com    — remote tech jobs (free API)
  • Arbeitnow.com   — EU + remote jobs (free API)
  • Jobicy.com      — remote jobs (free API)

  All three have free public APIs — no sign up needed.

──────────────────────────────────────────────────
 TIPS FOR BETTER EMAIL RESULTS
──────────────────────────────────────────────────
  The script guesses emails like careers@company.com
  and hr@company.com. These are often correct.

  For better results (free):
  • Snov.io — 50 free lookups/month: https://snov.io
  • Apollo.io — free tier: https://apollo.io
  • LinkedIn — search "HR manager at [company]"
    and find their email from their profile

──────────────────────────────────────────────────
 TROUBLESHOOTING
──────────────────────────────────────────────────
  "ModuleNotFoundError" → run:  pip install [module]
  "Rate limit" from Groq → reduce MAX_JOBS to 15
  Excel not opening → install LibreOffice (free)

  Questions? The script has comments throughout!