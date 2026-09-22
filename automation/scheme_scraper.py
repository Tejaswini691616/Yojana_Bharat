# PATH: GovScheme/automation/scheme_scraper.py
"""
Scheme discovery / collection (spec section 23).

This module is the single integration point for "Official Government
Sources -> API / permitted scraping / RPA collection -> Data Parser".

For this offline, examiner-runnable prototype, it reads from a local
mock feed file (automation/mock_official_feed.json) that represents what
an official API/RSS feed would return. This is clearly a placeholder:

    - It does NOT scrape any real government website.
    - It NEVER bypasses CAPTCHA, OTP, biometrics, or login controls.
    - To go live, replace `fetch_candidate_schemes()` with a call to an
      official government API/open-data feed (preferred) or a scraper
      that respects that source's terms of use and robots.txt.

Swap the mock feed for a live source without touching the rest of the
pipeline (validator / change_detector / scheduler stay the same).
"""
import json
import os

MOCK_FEED_PATH = os.path.join(os.path.dirname(__file__), "mock_official_feed.json")


def fetch_candidate_schemes() -> list:
    """Returns a list of candidate scheme dicts in the same shape as the
    `schemes` table's tracked fields. Source: local mock feed (offline demo)."""
    if not os.path.exists(MOCK_FEED_PATH):
        return []
    with open(MOCK_FEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
