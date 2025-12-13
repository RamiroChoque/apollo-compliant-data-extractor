# exporter.py
import csv

FIELDS = [
    "first_name", "last_name", "job_title",
    "company_name", "company_website", "industry",
    "email", "email_verified",
    "mobile_phone", "mobile_verified",
    "linkedin_url", "source"
]

def export_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
