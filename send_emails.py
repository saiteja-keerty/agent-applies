"""
╔══════════════════════════════════════════════════════╗
║           EMAIL SENDER FOR JOB APPLICATIONS          ║
║    Reads Excel file and sends personalized emails    ║
║         to hiring teams with full context            ║
╚══════════════════════════════════════════════════════╝

HOW TO USE:
  1. Run job_hunter.py (creates job_applications.xlsx)
  2. Open job_applications.xlsx and mark jobs as "Applied" 
     in the Status column (the ones you want to send emails to)
  3. python send_emails.py
  4. Preview emails BEFORE sending (DRY_RUN = True)
  5. Change DRY_RUN = False when ready to actually send

GMAIL SETUP (recommended):
  1. Enable 2-Step Verification: https://myaccount.google.com/security
  2. Get App Password: https://myaccount.google.com/apppasswords
  3. Paste the app password (16 chars) into SENDER_PASSWORD below
  4. Set SENDER_EMAIL = "yourname@gmail.com"

ALTERNATIVE: Use your own email provider (Outlook, Yahoo, etc.)
"""

import smtplib
import openpyxl
import time
import os
import base64
import json
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ─────────────────────────────────────────────
#  YOUR EMAIL CONFIGURATION — EDIT THESE
# ─────────────────────────────────────────────

SENDER_EMAIL    = "saiteja.keerty@gmail.com"      # Your Gmail or email
SENDER_PASSWORD = "kvqx howr gfdg fpsv"       # Gmail App Password (16 chars)
SENDER_NAME     = "Saiteja Keerty"                   # Your name
SENDER_PHONE    = "203-901-6018"              # Your phone number
RESUME_FILE     = "Saiteja_keerty_Resume.pdf" # Your resume file (paste your resume as PDF in this folder)

# Email settings
SMTP_HOST       = "smtp.gmail.com"             # Gmail SMTP
SMTP_PORT       = 587                          # TLS port
DRY_RUN         = True                        # Set to False to ACTUALLY send emails
MAX_EMAILS      = 5                            # Limit number of emails to send (set to None for all)
                                                # First run with True to preview!

# SEND ALL JOBS: Automatically sends to all jobs in Excel

# Input/Output files
PROJECT_FOLDER  = os.path.dirname(os.path.abspath(__file__))  # Script's folder
INPUT_FILE      = os.path.join(PROJECT_FOLDER, "job_applications.xlsx")  # From job_hunter.py
OUTPUT_FILE     = os.path.join(PROJECT_FOLDER, "send_log.txt")  # Log of what was sent

# DUPLICATE PREVENTION
SENT_LOG_FILE   = os.path.join(PROJECT_FOLDER, "sent_emails.json")  # Track sent emails

# API Keys for email finding
HUNTER_API_KEY  = os.getenv("HUNTER_API_KEY", "YOUR_HUNTER_API_KEY_HERE")  # Hunter.io API key

# Email template — this will be used for ALL emails
# {company}, {job_title}, {job_url}, {cover_letter} will be replaced with actual data
EMAIL_BODY_TEMPLATE = """Hello,

I hope you are doing well.

I am writing to express my strong interest in the {job_title} position at {company}. With dedicated experience in data engineering, I have worked for both startups and multinational companies (MNCs) where I specialized in building systems from scratch and developing end-to-end pipelines. My background includes successfully delivering R&D projects and proofs of concept (POCs).

I bring significant expertise in:
• Databricks & Cloud platforms (AWS, Azure, GCP)
• ETL pipelines & data architecture
• Languages: Python, SQL, Data Science and AI tools
• Infrastructure tools: Airflow, Terraform
• Startup & MNC experience in R&D projects and building POCs

I am confident that my skills and experience align closely with what you're looking for. Please find my resume attached for your review.

I am available to start immediately and would welcome the opportunity to discuss how my background can contribute to your team.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
{sender_name}
{sender_phone}
{sender_email}

---
Sent using own Job Agent - open source built by me - sorry if spammed you!:
"""

# ─────────────────────────────────────────────
#  📧  EMAIL SENDER LOGIC
# ─────────────────────────────────────────────

def load_sent_emails():
    """Load previously sent emails to prevent duplicates."""
    if os.path.exists(SENT_LOG_FILE):
        try:
            with open(SENT_LOG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_sent_email(company, job_title, email):
    """Save sent email to prevent future duplicates."""
    sent_emails = load_sent_emails()
    key = f"{company.lower()}|{job_title.lower()}|{email.lower()}"
    sent_emails[key] = {
        "company": company,
        "job_title": job_title,
        "email": email,
        "sent_date": datetime.now().isoformat()
    }
    
    with open(SENT_LOG_FILE, 'w') as f:
        json.dump(sent_emails, f, indent=2)


def is_email_already_sent(company, job_title, email):
    """Check if email was already sent to prevent duplicates."""
    sent_emails = load_sent_emails()
    key = f"{company.lower()}|{job_title.lower()}|{email.lower()}"
    return key in sent_emails


def update_excel_status(row_number, status):
    """Update the status column in Excel for sent emails."""
    try:
        wb = openpyxl.load_workbook(INPUT_FILE)
        ws = wb["Applications"]
        ws.cell(row=row_number, column=1, value=status)
        wb.save(INPUT_FILE)
    except Exception as e:
        print(f"    ⚠️  Could not update Excel status: {e}")


def read_excel(filename: str) -> list[dict]:
    """Read job data from Excel file."""
    wb = openpyxl.load_workbook(filename)
    ws = wb["Applications"]
    
    jobs = []
    for row in ws.iter_rows(min_row=2, values_only=False):  # Skip header
        job = {
            "status":      row[0].value,
            "company":     row[1].value,
            "job_title":   row[2].value,
            "location":    row[3].value,
            "source":      row[4].value,
            "url":         row[5].value,
            "email_1":     row[6].value,
            "email_2":     row[7].value,
            "email_3":     row[8].value,
            "email_4":     row[9].value,
            "email_5":     row[10].value,
            "cover_letter":row[11].value,
            "date_found":  row[12].value,
            "notes":       row[13].value,
            "excel_row":   row[0].row,  # Track which row for later logging
        }
        jobs.append(job)
    
    return jobs


def build_email_body(job: dict, sender_name: str, sender_email: str, sender_phone: str) -> str:
    """Build full email body with context."""
    body = EMAIL_BODY_TEMPLATE.format(
        job_title=job.get("job_title", ""),
        company=job.get("company", ""),
        sender_name=sender_name,
        sender_email=sender_email,
        sender_phone=sender_phone,
    )
    return body


# Additional email finding functions (copied from job_hunter.py)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def get_domain_from_url(url: str) -> str:
    """Extract domain from a URL."""
    if not url:
        return ""
    url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    return url.split("/")[0].strip()


def guess_emails(company: str, company_url: str) -> list[str]:
    """
    Generate a list of likely email addresses for a company.
    These are guesses — you verify manually before sending.
    """
    domain = get_domain_from_url(company_url)
    if not domain or len(domain) < 4:
        # Try to build domain from company name
        clean = re.sub(r'[^a-zA-Z0-9]', '', company.lower().split()[0])
        domain = f"{clean}.com"

    # Generate HR/careers emails (these are safe generic guesses)
    emails = [
        f"careers@{domain}",
        f"hr@{domain}",
        f"recruiting@{domain}",
        f"hiring@{domain}",
        f"jobs@{domain}",
    ]
    return emails


def scrape_emails_from_url(url: str) -> list[str]:
    """
    Scrape emails from a given URL.
    """
    if not url:
        return []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()
        # Find all emails using regex
        email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        # Filter valid emails
        valid_emails = [email for email in emails if verify_email_syntax(email)]
        # Remove duplicates and return
        return list(set(valid_emails))
    except Exception as e:
        print(f"    ⚠️  Error scraping {url}: {e}")
        return []


def get_emails_from_hunter(domain: str) -> list[str]:
    """
    Get emails from Hunter.io domain search.
    """
    if not HUNTER_API_KEY or not domain:
        return []
    try:
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        emails = []
        for email_data in data.get("data", {}).get("emails", []):
            email = email_data.get("value")
            if email and verify_email_syntax(email):
                emails.append(email)
        return emails[:10]  # limit to 10
    except Exception as e:
        print(f"    ⚠️  Hunter.io error for {domain}: {e}")
        return []


def search_linkedin_professionals(job_title: str, company: str) -> list[str]:
    """
    Search LinkedIn for professionals (HR/hiring managers) via Google search.
    Uses site:linkedin.com search to find relevant profiles and emails.
    """
    emails = []
    try:
        # Search for HR professionals at the company
        search_queries = [
            f"site:linkedin.com {company} HR hiring manager",
            f"site:linkedin.com {company} recruiting",
            f"site:linkedin.com {company} \"recruiter\" email",
            f"site:linkedin.com {company} CEO",
            f"site:linkedin.com {company} CTO",
            f"site:linkedin.com {company} head of engineering",
            f"site:linkedin.com {company} talent acquisition",
        ]
        
        for query in search_queries:
            try:
                # Use Google Custom Search via requests with proper headers
                google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                resp = requests.get(google_url, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Extract emails from search results
                email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
                found_emails = re.findall(email_pattern, resp.text)
                emails.extend([e for e in found_emails if verify_email_syntax(e)])
                time.sleep(0.5)  # be respectful
            except Exception as e:
                continue
        
        return list(set(emails))[:10]  # deduplicate and limit
    except Exception as e:
        print(f"    ⚠️  LinkedIn search error: {e}")
        return []


def search_google_for_emails(job_title: str, company: str) -> list[str]:
    """
    Search Google for professional emails related to job title and company.
    Targets HR, hiring managers, recruiters, etc.
    """
    emails = []
    try:
        search_queries = [
            f"{company} {job_title} HR email contact",
            f"{company} hiring manager {job_title} email",
            f"{company} \"careers@\" OR \"hr@\" OR \"recruiting@\"",
            f"{company} recruiter contact email",
            f"{company} CEO email",
            f"{company} CTO email",
            f"{company} head of engineering email",
            f"{company} talent acquisition email",
        ]
        
        for query in search_queries:
            try:
                # Use Google search
                google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                resp = requests.get(google_url, headers=HEADERS, timeout=10)
                
                # Extract emails from search results
                email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
                found_emails = re.findall(email_pattern, resp.text)
                emails.extend([e for e in found_emails if verify_email_syntax(e)])
                time.sleep(0.5)  # be respectful
            except Exception as e:
                continue
        
        return list(set(emails))[:15]  # deduplicate and limit to 15
    except Exception as e:
        print(f"    ⚠️  Google search error: {e}")
        return []


def search_professional_networks(company: str, job_title: str) -> list[str]:
    """
    Search multiple professional networks and job boards for emails.
    Looks for contact pages, careers pages, team listings.
    """
    emails = []
    domain = get_domain_from_url(f"https://{company.lower().replace(' ', '')}.com")
    
    # Common professional contact page paths
    contact_paths = [
        "/careers",
        "/about/team",
        "/contact",
        "/company",
        "/about",
        "/jobs",
        "/hr",
        "/recruiting",
        "/team",
        "/leadership",
    ]
    
    for path in contact_paths:
        try:
            # Try common company domain structures
            urls_to_try = [
                f"https://{domain}{path}",
                f"https://www.{domain}{path}",
            ]
            
            for url in urls_to_try:
                try:
                    resp = requests.get(url, headers=HEADERS, timeout=5)
                    # Extract emails
                    email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
                    found_emails = re.findall(email_pattern, resp.text)
                    emails.extend([e for e in found_emails if verify_email_syntax(e)])
                except:
                    continue
            time.sleep(0.3)
        except Exception as e:
            continue
    
    return list(set(emails))[:10]


def verify_email_syntax(email: str) -> bool:
    """Basic syntax check."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def find_additional_emails(job: dict) -> list[str]:
    """Find additional emails for a job by searching Google, LinkedIn, etc."""
    company = job.get("company", "")
    job_title = job.get("title", job.get("job_title", ""))
    company_url = job.get("company_url", job.get("url", ""))

    print(f"    🔍 Finding additional emails for {company}...")

    # Scrape emails from company website and job posting
    scraped = []
    urls_to_scrape = [company_url, job.get("url", "")]
    for url in urls_to_scrape:
        if url:
            scraped.extend(scrape_emails_from_url(url))
            time.sleep(0.5)

    # Get emails from Hunter.io
    domain = get_domain_from_url(company_url)
    hunter_emails = get_emails_from_hunter(domain)

    # Search LinkedIn for HR professionals
    linkedin_emails = search_linkedin_professionals(job_title, company)

    # Search Google for emails
    google_emails = search_google_for_emails(job_title, company)

    # Search professional networks (careers pages, team pages, etc)
    network_emails = search_professional_networks(company, job_title)

    # Guess emails (last resort)
    guessed = guess_emails(company, company_url)

    # Combine and deduplicate
    all_emails = list(set(scraped + hunter_emails + linkedin_emails + google_emails + network_emails + guessed))
    print(f"    Found {len(all_emails)} additional emails")
    return all_emails[:20]  # limit to 20 additional emails


def send_email(recipient_email: str, job: dict, sender_email: str, sender_password: str, 
               sender_name: str, sender_phone: str, dry_run: bool = True) -> dict:
    """Send an individual email."""
    
    subject = f"Application: {job['job_title']} at {job['company']} - 5 years"
    body = build_email_body(job, sender_name, sender_email, sender_phone)
    
    result = {
        "company": job["company"],
        "job_title": job["job_title"],
        "recipient": recipient_email,
        "status": "PREVIEW" if dry_run else "SENT",
        "timestamp": datetime.now().isoformat(),
        "error": None,
    }
    
    if dry_run:
        print(f"\n{'='*70}")
        print(f"DRY RUN — Would send to: {recipient_email}")
        print(f"{'='*70}")
        print(f"TO: {recipient_email}")
        print(f"SUBJECT: {subject}")
        print(f"FROM: {sender_name} <{sender_email}>")
        if os.path.exists(RESUME_FILE):
            print(f"ATTACHMENT: {RESUME_FILE}")
        print(f"\n{body}")
        print(f"{'='*70}\n")
        return result
    
    # Actually send email
    try:
        msg = MIMEMultipart()
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        # Attach resume if it exists
        if os.path.exists(RESUME_FILE):
            with open(RESUME_FILE, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {RESUME_FILE}")
            msg.attach(part)
        
        print(f"  Sending to {recipient_email}...", end=" ")
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print("Sent!")
        return result
    
    except Exception as e:
        print(f"Failed: {e}")
        result["status"] = "FAILED"
        result["error"] = str(e)
        return result


def log_results(results: list[dict], filename: str):
    """Save email sending log."""
    with open(filename, "w") as f:
        f.write("EMAIL SENDING LOG\n")
        f.write("="*70 + "\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        
        for result in results:
            f.write(f"Company: {result['company']}\n")
            f.write(f"Job: {result['job_title']}\n")
            f.write(f"Recipient: {result['recipient']}\n")
            f.write(f"Status: {result['status']}\n")
            if result['error']:
                f.write(f"Error: {result['error']}\n")
            f.write(f"Time: {result['timestamp']}\n")
            f.write("-"*70 + "\n\n")
    
    print(f"  Log saved to: {filename}")


# ─────────────────────────────────────────────
#  🚀  MAIN RUNNER
# ─────────────────────────────────────────────

def main():
    print("\n" + "="*70)
    print("  EMAIL SENDER FOR JOB APPLICATIONS")
    print("="*70 + "\n")
    
    # Safety check
    if DRY_RUN:
        print("  WARNING: DRY RUN MODE — Just showing what WOULD be sent")
        print("  Set DRY_RUN = False in the script to actually send emails\n")
    else:
        confirm = input("  WARNING: REAL SEND MODE — Actually send emails? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("  Cancelled.")
            return
    
    # Load jobs
    print(f"  Reading {INPUT_FILE}...")
    jobs = read_excel(INPUT_FILE)
    
    if not jobs:
        print(f"  WARNING: No jobs found in Excel!")
        print(f"  Please run job_hunter.py to scrape jobs first.")
        return
    
    print(f"  Found {len(jobs)} jobs in Excel")
    if MAX_EMAILS:
        jobs = jobs[:MAX_EMAILS]
        print(f"  Limiting to first {MAX_EMAILS} jobs")
    print(f"  Checking for duplicate emails...\n")
    
    all_results = []
    
    # Send emails to ALL jobs
    for i, job in enumerate(jobs, 1):
        print(f"  [{i}/{len(jobs)}] {job['company']} — {job['job_title']}")
        
        # Determine target email(s) to try
        emails_to_try = [job["email_1"], job["email_2"], job["email_3"], job["email_4"], job["email_5"]]
        emails_to_try = [email for email in emails_to_try if email]  # Remove empty emails
        
        # Find additional emails from Google, LinkedIn, etc.
        additional_emails = find_additional_emails(job)
        emails_to_try.extend(additional_emails)
        
        # Remove duplicates
        emails_to_try = list(set(emails_to_try))
        
        if not emails_to_try:
            print(f"    WARNING: No email found, skipping...")
            continue
        
        # Try each email address until one succeeds
        email_sent = False
        for target_email in emails_to_try:
            # Check for duplicates
            if is_email_already_sent(job["company"], job["job_title"], target_email):
                print(f"    WARNING: Already sent to {target_email}, trying next...")
                continue
            
            print(f"    Trying: {target_email}")
            result = send_email(
                recipient_email=target_email,
                job=job,
                sender_email=SENDER_EMAIL,
                sender_password=SENDER_PASSWORD,
                sender_name=SENDER_NAME,
                sender_phone=SENDER_PHONE,
                dry_run=DRY_RUN
            )
            
            # Mark as sent if successful
            if result["status"] == "SENT" and not DRY_RUN:
                save_sent_email(job["company"], job["job_title"], target_email)
                # Update Excel status
                update_excel_status(job["excel_row"], "Sent")
                email_sent = True
                print(f"    SUCCESS: Email sent to {target_email}")
                break  # Stop trying other emails for this job
            else:
                print(f"    FAILED: Could not send to {target_email}")
        
        if not email_sent and not DRY_RUN:
            print(f"    ERROR: Failed to send to any email address for this job")
            # Still add to results for logging
            result = {
                "company": job["company"],
                "job_title": job["job_title"],
                "recipient": " | ".join(emails_to_try),
                "status": "FAILED",
                "timestamp": datetime.now().isoformat(),
                "error": "All email addresses failed",
            }
            all_results.append(result)
            continue
        
        if not DRY_RUN:
            time.sleep(2)  # Rate limit — don't spam
    
    # Summary
    print("\n" + "="*70)
    if DRY_RUN:
        print(f"  PREVIEW COMPLETE — {len(all_results)} emails shown above")
        print("\n  NEXT STEPS:")
        print("  1. Review the email previews above")
        print("  2. If they look good, change DRY_RUN = False")
        print("  3. Run this script again to send for real")
    else:
        sent = len([r for r in all_results if r["status"] == "SENT"])
        failed = len([r for r in all_results if r["status"] == "FAILED"])
        print(f"  Sent to companies: {sent} emails")
        if failed:
            print(f"  Failed: {failed} emails")
    
    print("="*70 + "\n")
    
    # Log results
    log_results(all_results, OUTPUT_FILE)


if __name__ == "__main__":
    main()
