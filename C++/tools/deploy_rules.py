"""
Publish firestore.rules without the Firebase CLI's database check.

The CLI tries to create "(default)" even when the database already exists, and
that path asks for billing. The Rules API deploys the same rules, free.

    python tools/deploy_rules.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT = "cpp-lab-faith-praise"
ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "firestore.rules"
CONFIGSTORE = Path(os.path.expanduser("~/.config/configstore/firebase-tools.json"))


def api(method: str, url: str, body: dict | None = None) -> tuple[int, dict]:
    token = json.loads(CONFIGSTORE.read_text(encoding="utf-8"))["tokens"]["access_token"]
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT,
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode() or "{}"
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw[:400]}


def main() -> int:
    source = RULES.read_text(encoding="utf-8")

    status, body = api("POST", f"https://firebaserules.googleapis.com/v1/projects/{PROJECT}/rulesets", {
        "source": {"files": [{"name": "firestore.rules", "content": source}]}
    })
    if status != 200:
        print(f"could not create the ruleset ({status}): {json.dumps(body)[:300]}")
        return 1
    ruleset = body["name"]
    print(f"  ruleset created: ...{ruleset[-24:]}")

    status, body = api("POST",
                       f"https://firebaserules.googleapis.com/v1/projects/{PROJECT}/releases?releaseId=cloud.firestore",
                       {"release": {"name": f"projects/{PROJECT}/releases/cloud.firestore",
                                    "rulesetName": ruleset}})
    if status != 200:
        # the release already exists: point it at the new ruleset instead
        status, body = api("PATCH",
                           f"https://firebaserules.googleapis.com/v1/projects/{PROJECT}/releases/cloud.firestore",
                           {"release": {"name": f"projects/{PROJECT}/releases/cloud.firestore",
                                        "rulesetName": ruleset}})
    if status != 200:
        print(f"could not publish the release ({status}): {json.dumps(body)[:300]}")
        return 1
    print("  release cloud.firestore now points at that ruleset")

    status, body = api("GET", f"https://firebaserules.googleapis.com/v1/projects/{PROJECT}/releases")
    for rel in body.get("releases", []):
        print(f"  live: {rel['name'].split('/')[-1]} -> ...{rel.get('rulesetName','')[-12:]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
