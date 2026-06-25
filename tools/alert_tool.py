import os
from datetime import datetime

def create_alert(severity: str, title: str, description: str, metrics: dict) -> dict:
    timestamp = datetime.utcnow().isoformat()

    alert = {
        "alert_id": f"alert-{timestamp[:10]}-{severity}",
        "severity": severity,
        "title": title,
        "description": description,
        "metrics": metrics,
        "timestamp": timestamp,
        "status": "open"
    }

    print(f"\n[ALERT] {severity.upper()}: {title}")
    print(f"  Description: {description}")
    print(f"  Time: {timestamp}")

    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO")

    if github_token and github_repo:
        try:
            import httpx
            response = httpx.post(
                f"https://api.github.com/repos/{github_repo}/issues",
                headers={
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "title": f"[{severity.upper()}] {title}",
                    "body": f"{description}\n\nMetrics:\n```json\n{str(metrics)}\n```\n\nDetected at: {timestamp}"
                }
            )
            if response.status_code == 201:
                alert["github_issue_url"] = response.json()["html_url"]
                print(f"  GitHub issue created: {alert['github_issue_url']}")
        except Exception as e:
            print(f"  GitHub issue creation skipped: {e}")
    else:
        print("  GitHub issue creation skipped: no GITHUB_TOKEN set")

    return alert