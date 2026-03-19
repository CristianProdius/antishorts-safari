#!/usr/bin/env python3
"""
Sets ALL App Store Connect metadata via the API.
Called automatically by deploy.sh after a successful upload.

Sets: description, keywords, support URL, privacy URL, marketing URL,
      promotional text, review notes, and contact info.

Usage: python3 scripts/set-review-notes.py
"""

import jwt
import time
import requests
import os
import sys
import json

# -- Configuration ------------------------------------------------------------
API_KEY_ID = "32LF4Q3Z7N"
API_ISSUER_ID = "3c8dce31-6803-4d23-ba4f-48dab97d8d98"
APP_APPLE_ID = "6760815295"

KEY_PATH = os.path.expanduser(f"~/.appstoreconnect/private_keys/AuthKey_{API_KEY_ID}.p8")
BASE_URL = "https://api.appstoreconnect.apple.com/v1"

# -- App Store Metadata -------------------------------------------------------

DESCRIPTION = """AntiShorts removes YouTube Shorts from your browsing experience in Safari.

Shorts shelves on the homepage, Shorts in search results, the Shorts sidebar link, the Shorts tab on channels — all hidden automatically.

Direct /shorts/ links are redirected to the standard video player so you can watch in a normal, distraction-free format.

Features:
• Blocks Shorts from the homepage, search, and sidebar
• Redirects /shorts/ URLs to the regular video player
• One-click toggle to pause blocking
• No data collected — everything runs locally on your Mac
• Lightweight — uses CSS, JavaScript, and Safari's declarativeNetRequest API

Take back control of your YouTube experience."""

KEYWORDS = "youtube,shorts,blocker,safari,extension,content,filter,distraction,focus,productivity"
SUBTITLE = "Block YouTube Shorts in Safari"
PROMOTIONAL_TEXT = "Remove YouTube Shorts from your feed. No Shorts shelves, no Shorts in search, no Shorts sidebar link. Direct Shorts URLs redirect to the normal video player."

SUPPORT_URL = "https://cristianprodius.github.io/antishorts-safari/support.html"
MARKETING_URL = "https://cristianprodius.github.io/antishorts-safari/"
PRIVACY_URL = "https://cristianprodius.github.io/antishorts-safari/privacy.html"

COPYRIGHT = "2026 Prodius"

REVIEW_NOTES = """How to test this Safari Web Extension:

1. Build and run the app (it launches a helper window)
2. Open Safari → Settings → Extensions
3. Enable "AntiShorts"
4. Grant permission for youtube.com when prompted
5. Visit youtube.com — Shorts shelf and sidebar link should be hidden
6. Try visiting youtube.com/shorts/dQw4w9WgXcQ — it should redirect to youtube.com/watch?v=dQw4w9WgXcQ
7. Click the extension icon in the Safari toolbar to toggle blocking on/off

No login or account required. The extension collects no data."""

# Review contact info
REVIEW_FIRST_NAME = "Cristian"
REVIEW_LAST_NAME = "Prodius"
REVIEW_EMAIL = ""       # Will be fetched from git config if empty
REVIEW_PHONE = "+37368200722"

# -- Helpers ------------------------------------------------------------------

def log(level, msg):
    colors = {"INFO": "\033[0;34m", "OK": "\033[0;32m", "WARN": "\033[1;33m", "ERROR": "\033[0;31m"}
    nc = "\033[0m"
    print(f"{colors.get(level, '')}{f'[{level}]'}{nc} {msg}", file=sys.stderr)


def generate_token():
    with open(KEY_PATH, "r") as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        "iss": API_ISSUER_ID,
        "iat": now,
        "exp": now + 1200,
        "aud": "appstoreconnect-v1",
    }
    return jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": API_KEY_ID})


def api(method, path, token, data=None):
    headers = {"Authorization": f"Bearer {token}"}
    if data:
        headers["Content-Type"] = "application/json"

    resp = requests.request(method, f"{BASE_URL}{path}", headers=headers, json=data)

    if not resp.ok:
        log("ERROR", f"API {method} {path} → {resp.status_code}")
        try:
            errors = resp.json().get("errors", [])
            for err in errors:
                log("ERROR", f"  {err.get('title', '')}: {err.get('detail', '')}")
        except Exception:
            log("ERROR", f"  {resp.text[:500]}")
        resp.raise_for_status()

    return resp.json() if resp.content else {}


# -- Main ---------------------------------------------------------------------

def main():
    log("INFO", "Generating API token...")
    token = generate_token()

    # ── 1. Find editable App Store version ──────────────────────────────────
    log("INFO", "Fetching app store versions...")
    versions_resp = api("GET", f"/apps/{APP_APPLE_ID}/appStoreVersions", token)

    editable_states = {
        "PREPARE_FOR_SUBMISSION", "DEVELOPER_REJECTED",
        "REJECTED", "METADATA_REJECTED", "WAITING_FOR_REVIEW",
    }
    editable = [
        v for v in versions_resp.get("data", [])
        if v["attributes"]["appStoreState"] in editable_states
    ]

    if not editable:
        states = [v["attributes"]["appStoreState"] for v in versions_resp.get("data", [])]
        log("WARN", f"No editable version found. States: {states}")
        log("WARN", "Metadata not set. Wait for the build to process and try again.")
        sys.exit(0)

    version = editable[0]
    version_id = version["id"]
    version_num = version["attributes"]["versionString"]
    version_state = version["attributes"]["appStoreState"]
    log("OK", f"Found version {version_num} (state: {version_state}, id: {version_id})")

    # ── 2. Update App Info (copyright, privacy URL) ─────────────────────────
    log("INFO", "Updating app info...")
    # Get app info
    app_infos = api("GET", f"/apps/{APP_APPLE_ID}/appInfos", token)
    if app_infos.get("data"):
        app_info_id = app_infos["data"][0]["id"]
        # Get app info localizations
        localizations = api("GET", f"/appInfos/{app_info_id}/appInfoLocalizations", token)
        if localizations.get("data"):
            loc_id = localizations["data"][0]["id"]
            api("PATCH", f"/appInfoLocalizations/{loc_id}", token, {
                "data": {
                    "type": "appInfoLocalizations",
                    "id": loc_id,
                    "attributes": {
                        "subtitle": SUBTITLE,
                        "privacyPolicyUrl": PRIVACY_URL,
                    }
                }
            })
            log("OK", "App info localization updated (subtitle, privacy URL)")

    # ── 2b. Set copyright on the version ───────────────────────────────────
    log("INFO", "Setting copyright...")
    api("PATCH", f"/appStoreVersions/{version_id}", token, {
        "data": {
            "type": "appStoreVersions",
            "id": version_id,
            "attributes": {
                "copyright": COPYRIGHT,
            }
        }
    })
    log("OK", f"Copyright set: {COPYRIGHT}")

    # ── 2c. Set export compliance on latest build ───────────────────────────
    log("INFO", "Setting export compliance...")
    builds_resp = api("GET", f"/builds?filter[app]={APP_APPLE_ID}&sort=-uploadedDate&limit=1", token)
    if builds_resp.get("data"):
        build_id = builds_resp["data"][0]["id"]
        try:
            api("PATCH", f"/builds/{build_id}", token, {
                "data": {
                    "type": "builds",
                    "id": build_id,
                    "attributes": {
                        "usesNonExemptEncryption": False,
                    }
                }
            })
            log("OK", "Export compliance set (no encryption)")
        except Exception:
            log("WARN", "Could not set export compliance (build may still be processing)")

    # ── 3. Update Version Localization (description, keywords, etc.) ────────
    log("INFO", "Updating version localization...")
    loc_resp = api("GET", f"/appStoreVersions/{version_id}/appStoreVersionLocalizations", token)

    if loc_resp.get("data"):
        loc_id = loc_resp["data"][0]["id"]
        attrs = {
            "description": DESCRIPTION,
            "keywords": KEYWORDS,
            "marketingUrl": MARKETING_URL,
            "promotionalText": PROMOTIONAL_TEXT,
            "supportUrl": SUPPORT_URL,
        }
        # whatsNew can only be set on updates, not the first version
        if version_num != "1.0" and version_num != "1.0.0":
            attrs["whatsNew"] = "Bug fixes and improvements."

        api("PATCH", f"/appStoreVersionLocalizations/{loc_id}", token, {
            "data": {
                "type": "appStoreVersionLocalizations",
                "id": loc_id,
                "attributes": attrs,
            }
        })
        log("OK", "Version localization updated (description, keywords, URLs, promo text)")
    else:
        log("WARN", "No version localizations found")

    # ── 4. Set Review Notes & Contact Info ──────────────────────────────────
    log("INFO", "Setting review notes...")

    # Resolve email from git config if not set
    email = REVIEW_EMAIL
    if not email:
        try:
            import subprocess
            email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
        except Exception:
            email = ""

    review_attrs = {"notes": REVIEW_NOTES}
    if REVIEW_FIRST_NAME:
        review_attrs["contactFirstName"] = REVIEW_FIRST_NAME
    if REVIEW_LAST_NAME:
        review_attrs["contactLastName"] = REVIEW_LAST_NAME
    if email:
        review_attrs["contactEmail"] = email
    if REVIEW_PHONE:
        review_attrs["contactPhone"] = REVIEW_PHONE

    # Try to get existing review detail, create if not found
    need_create = False
    try:
        review_detail = api("GET", f"/appStoreVersions/{version_id}/appStoreReviewDetail", token)
        if review_detail and review_detail.get("data") and review_detail["data"].get("id"):
            review_detail_id = review_detail["data"]["id"]
            api("PATCH", f"/appStoreReviewDetails/{review_detail_id}", token, {
                "data": {
                    "type": "appStoreReviewDetails",
                    "id": review_detail_id,
                    "attributes": review_attrs,
                }
            })
        else:
            need_create = True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in (404, 500):
            need_create = True
        else:
            raise

    if need_create:
        api("POST", "/appStoreReviewDetails", token, {
            "data": {
                "type": "appStoreReviewDetails",
                "attributes": review_attrs,
                "relationships": {
                    "appStoreVersion": {
                        "data": {
                            "type": "appStoreVersions",
                            "id": version_id,
                        }
                    }
                }
            }
        })

    log("OK", "Review notes and contact info set")

    # ── 5. Summary ──────────────────────────────────────────────────────────
    print()
    log("OK", "All App Store metadata set successfully!")
    print()
    log("INFO", "What was set:")
    log("INFO", f"  Description:      {len(DESCRIPTION)} chars")
    log("INFO", f"  Keywords:         {KEYWORDS}")
    log("INFO", f"  Subtitle:         {SUBTITLE}")
    log("INFO", f"  Promotional Text: {PROMOTIONAL_TEXT[:60]}...")
    log("INFO", f"  Support URL:      {SUPPORT_URL}")
    log("INFO", f"  Marketing URL:    {MARKETING_URL}")
    log("INFO", f"  Privacy URL:      {PRIVACY_URL}")
    log("INFO", f"  Review Notes:     {len(REVIEW_NOTES)} chars")
    log("INFO", f"  Contact:          {REVIEW_FIRST_NAME} {REVIEW_LAST_NAME}")
    print()
    log("INFO", "Still need to set manually in App Store Connect:")
    log("INFO", "  • Screenshots (upload from screenshots/ folder)")
    log("INFO", "  • Age Rating (answer 'None' to all → 4+)")
    log("INFO", "  • Privacy Nutrition Labels (select 'Data Not Collected')")
    log("INFO", "  • Select the processed build")


if __name__ == "__main__":
    main()
