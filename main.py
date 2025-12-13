# main.py
import csv
from apollo_client import ApolloClient
from exporter import export_csv

INPUT = "input.csv"
OUTPUT = "sample_output.csv"

def main():
    client = ApolloClient(mobile_credit_budget=10)
    seen = set()
    results = []

    with open(INPUT, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            linkedin = row["linkedin_url"].strip()
            if linkedin in seen:
                continue

            result = client.process(
                linkedin_url=linkedin,
                name=row.get("name", ""),
                domain=row.get("company_domain", "")
            )

            results.append(result)
            seen.add(linkedin)

    export_csv(results, OUTPUT)
    print(f"[OK] {len(results)} unique records written to {OUTPUT}")

if __name__ == "__main__":
    main()
