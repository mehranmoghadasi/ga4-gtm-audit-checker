"""
ga4-gtm-audit-checker
Audits GA4 event coverage and GTM tag health.
Author: Mehran Moghadasi
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────
EXPECTED_EVENTS = [
    "page_view", "session_start", "first_visit",
    "scroll", "click", "file_download",
    "purchase", "add_to_cart", "begin_checkout",
    "generate_lead", "form_submit", "sign_up"
]

# ── GA4 Audit ─────────────────────────────────────────────────
def audit_ga4_events(property_id: str, credentials_path: str) -> dict:
    """Check GA4 for expected event coverage over the last 30 days."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Dimension, Metric
        )
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="eventCount")],
            date_ranges=[DateRange(
                start_date=(datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d"),
                end_date="today"
            )]
        )
        response = client.run_report(request)
        found_events = {
            row.dimension_values[0].value: int(row.metric_values[0].value)
            for row in response.rows
        }

        results = {}
        for event in EXPECTED_EVENTS:
            if event in found_events:
                results[event] = {"status": "ok", "count": found_events[event]}
            else:
                results[event] = {"status": "missing", "count": 0}

        return results

    except Exception as e:
        return {"error": str(e)}


# ── GTM Audit ─────────────────────────────────────────────────
def audit_gtm_tags(container_id: str, credentials_path: str) -> list:
    """List all GTM tags and flag paused or never-fired ones."""
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/tagmanager.readonly"]
        )
        service = build("tagmanager", "v2", credentials=creds)
        account_id = container_id.split("_")[0]
        tags = service.accounts().containers().workspaces().tags().list(
            parent=f"accounts/{account_id}/containers/{container_id}/workspaces/1"
        ).execute()

        tag_list = []
        for tag in tags.get("tag", []):
            tag_list.append({
                "name": tag.get("name"),
                "type": tag.get("type"),
                "paused": tag.get("paused", False),
                "firing_triggers": len(tag.get("firingTriggerId", [])),
                "last_modified": tag.get("fingerprint", "unknown")
            })
        return tag_list

    except Exception as e:
        return [{"error": str(e)}]


# ── Report Generator ──────────────────────────────────────────
def generate_report(ga4_results: dict, gtm_tags: list, output_format: str = "terminal"):
    """Print or export the audit report."""
    date_str = datetime.today().strftime("%Y-%m-%d")
    print(f"\nGA4 + GTM Audit Report — {date_str}")
    print("━" * 42)

    if "error" not in ga4_results:
        for event, data in ga4_results.items():
            icon = "✅" if data["status"] == "ok" else "❌"
            count = f"({data['count']:,} events)" if data["status"] == "ok" else "NOT FOUND"
            print(f"{icon} {event:<25} {count}")
    else:
        print(f"GA4 Error: {ga4_results['error']}")

    print("━" * 42)

    if gtm_tags and "error" not in gtm_tags[0]:
        active = sum(1 for t in gtm_tags if not t.get("paused"))
        paused = sum(1 for t in gtm_tags if t.get("paused"))
        no_trigger = sum(1 for t in gtm_tags if t.get("firing_triggers", 0) == 0)
        print(f"GTM Tags: {active} active | {paused} paused | {no_trigger} with no triggers")

        if output_format == "csv":
            import csv
            filename = f"audit_{date_str}.csv"
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["name", "type", "paused", "firing_triggers"])
                writer.writeheader()
                writer.writerows(gtm_tags)
            print(f"Report saved to: {filename}")

        elif output_format == "json":
            filename = f"audit_{date_str}.json"
            with open(filename, "w") as f:
                json.dump({"ga4": ga4_results, "gtm": gtm_tags}, f, indent=2)
            print(f"Report saved to: {filename}")
    else:
        print(f"GTM Error: {gtm_tags[0].get('error', 'Unknown') if gtm_tags else 'No data'}")


# ── CLI ───────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GA4 + GTM Audit Tool")
    parser.add_argument("--property", required=True, help="GA4 Property ID")
    parser.add_argument("--container", default=None, help="GTM Container ID")
    parser.add_argument("--credentials", default=os.getenv("GOOGLE_CREDENTIALS_PATH"),
                        help="Path to service account JSON")
    parser.add_argument("--output", choices=["terminal", "csv", "json"],
                        default="terminal", help="Output format")
    parser.add_argument("--events-only", action="store_true",
                        help="Only run GA4 event audit")
    args = parser.parse_args()

    ga4_data = audit_ga4_events(args.property, args.credentials)
    gtm_data = audit_gtm_tags(args.container, args.credentials) if args.container and not args.events_only else []
    generate_report(ga4_data, gtm_data, args.output)
