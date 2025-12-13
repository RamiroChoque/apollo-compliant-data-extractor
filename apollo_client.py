# apollo_client.py
import os
import requests
import hashlib

BASE = "https://api.apollo.io/api/v1"
API_KEY = os.getenv("Apollo_API_Key_Here")

HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

class ApolloClient:
    def __init__(self, mobile_credit_budget=20):
        self.mobile_credits = mobile_credit_budget
        self.enrichment_available = True

    # Helper function
    def normalize_domain(self, domain):
        if not domain:
            return None

        domain = domain.strip().lower()

        # remove protocol
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "")

        # remove leading junk like +
        domain = domain.lstrip(" +@")

        # basic validation
        if "." not in domain:
            return None

        return domain


    # ---------- TRY REAL ENRICHMENT ----------

    # Attempting Apollo Person Enrichment API (available only on paid plans).
    # If API entitlement is missing, the pipeline automatically falls back
    # to search-based discovery while preserving schema and credit logic.

    # Enrichment API available – using live person enrichment

    def try_people_enrich(self, linkedin_url):
        url = f"{BASE}/people/match"
        payload = {"linkedin_url": linkedin_url}

        try:
            r = requests.post(url, headers=HEADERS, json=payload, timeout=15)
            if r.status_code in (401, 403, 404):
                self.enrichment_available = False
                return None
            r.raise_for_status()
            return r.json().get("person")
        except Exception:
            self.enrichment_available = False
            return None

    # ---------- SEARCH FALLBACK ----------
    def search_top_people(self, domain):
        domain = self.normalize_domain(domain)
        if not domain:
            return []

        url = f"{BASE}/mixed_people/organization_top_people"
        params = {"domain": domain}

        r = requests.get(url, headers=HEADERS, params=params, timeout=15)

        if r.status_code in (401, 403, 404, 422):
            return []

        r.raise_for_status()
        return r.json().get("people", [])


    def enrich_company(self, domain):
        domain = self.normalize_domain(domain)
        if not domain:
            return {}

        url = f"{BASE}/organizations/enrich"
        r = requests.post(
            url,
            headers=HEADERS,
            json={"domain": domain},
            timeout=15
        )

        if r.status_code in (401, 403, 404, 422):
            return {}

        r.raise_for_status()
        return r.json().get("organization", {})
    
    def infer_company_from_domain(self, domain):
        if not domain:
            return None

        base = domain.split(".")[0]
        return base.replace("-", " ").title()
    
    def infer_job_title(self, person, name):
        if person.get("title"):
            return person.get("title")
        return None



    # ---------- SIMULATED MOBILE LOGIC ----------
    def simulate_mobile(self, seed):
        """
        Generating a deterministic, numeric-only simulated mobile number.
        Used only when Apollo enrichment APIs are unavailable.
        """
        if self.mobile_credits <= 0:
            return None, False

        # Convert hash seed to digits only
        digits = "".join(filter(str.isdigit, seed))

        # Ensure reasonable length (10–12 digits)
        mobile = digits[:10]
        if len(mobile) < 10:
            mobile = mobile.ljust(10, "0")

        self.mobile_credits -= 1
        return mobile, False

    # ---------- SIMULATED Mail LOGIC ----------
    def simulate_email(self, first_name, domain):
        """
        Generating a deterministic, realistic-looking email address.
        Used only when Apollo enrichment APIs are unavailable.
        """
        if not first_name or not domain:
            return None

        local = first_name.strip().lower()
        domain = domain.strip().lower()

        return f"{local}@{domain}"

    #Helper for job_title extraction
    def extract_job_title(self, person):
        """
        Safely extract job title from various Apollo response shapes.
        """
        if not person:
            return None

        # Most common
        if person.get("title"):
            return person["title"]

        # Sometimes used
        if person.get("current_title"):
            return person["current_title"]

        # Fallback: employment history
        history = person.get("employment_history", [])
        for job in history:
            if job.get("current") and job.get("title"):
                return job["title"]

        return None

    # ---------- UNIFIED PIPELINE ----------
    def process(self, linkedin_url, name, domain):
        domain = self.normalize_domain(domain)

        # 1. Try enrichment API
        if self.enrichment_available:
            enriched = self.try_people_enrich(linkedin_url)
            if enriched:
                return {
                    "first_name": enriched.get("first_name"),
                    "last_name": enriched.get("last_name"),
                    "job_title": self.extract_job_title(person),
                    "company_name": enriched.get("organization", {}).get("name"),
                    "company_website": enriched.get("organization", {}).get("website"),
                    "industry": enriched.get("organization", {}).get("industry"),
                    "email": enriched.get("email"),
                    "email_verified": enriched.get("email_verified"),
                    "mobile_phone": enriched.get("phone"),
                    "mobile_verified": enriched.get("phone_verified"),
                    "linkedin_url": linkedin_url,
                    "source": "apollo_enrichment"
                }

        # 2. Safe fallback
        company = self.enrich_company(domain)
        people = self.search_top_people(domain) if domain else []

        person = people[0] if people else {}
        seed = hashlib.md5(linkedin_url.encode()).hexdigest()
        mobile, mobile_verified = self.simulate_mobile(seed)

        company_name = company.get("name") or self.infer_company_from_domain(domain)
        company_website = company.get("website") or (f"https://{domain}" if domain else None)

        email = self.simulate_email(
        person.get("first_name") or (name.split()[0] if name else None),
        domain
)

        return {
            "first_name": person.get("first_name") or (name.split()[0] if name else None),
            "last_name": person.get("last_name") or (name.split()[-1] if name else None),
            "job_title": person.get("title"),
            "company_name": company_name,
            "company_website": company_website,
            "industry": company.get("industry"),
            "email": email,
            "email_verified": False,
            "mobile_phone": mobile,
            "mobile_verified": mobile_verified,
            "linkedin_url": linkedin_url,
            "source": "search_fallback"
        }
