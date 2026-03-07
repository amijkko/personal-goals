#!/usr/bin/env python3
"""Daily CRM enrichment: scan journal/, meetings/, kb/ for new mentions of contacts."""
import os
import sys
import re
from datetime import datetime, timezone, timedelta

GOALS_DIR = os.path.expanduser("~/goals")
BOT_DIR = os.path.expanduser("~/telegram-backlog-bot")
sys.path.insert(0, BOT_DIR)

DATABASE_URL = os.environ.get("CRM_DATABASE_URL") or os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("No DATABASE_URL set, skipping CRM enrichment")
    sys.exit(0)

os.environ["DATABASE_URL"] = DATABASE_URL

try:
    from crm_db import get_conn, find_contact, add_interaction, add_fact
    import psycopg2.extras
except ImportError:
    print("crm_db not available, skipping")
    sys.exit(0)

MOSCOW_TZ = timezone(timedelta(hours=3))
TODAY = datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")


def get_all_contacts():
    """Get all contact names from DB."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name FROM contacts ORDER BY id")
    contacts = cur.fetchall()
    # Also get aliases
    cur.execute("SELECT contact_id, alias FROM contact_aliases")
    aliases = {}
    for r in cur.fetchall():
        aliases.setdefault(r["contact_id"], []).append(r["alias"])
    cur.close()
    conn.close()
    return contacts, aliases


def get_existing_interactions(contact_id):
    """Get existing interaction summaries to avoid dupes."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT summary FROM interactions WHERE contact_id = %s", (contact_id,))
    result = {r[0] for r in cur.fetchall()}
    cur.close()
    conn.close()
    return result


def scan_file(filepath, contact_name, first_word):
    """Find lines mentioning a contact in a file."""
    mentions = []
    try:
        with open(filepath, "r") as f:
            content = f.read()
        if first_word.lower() not in content.lower():
            return []
        for line in content.split("\n"):
            if first_word.lower() in line.lower() and line.strip():
                clean = line.strip().lstrip("- ").lstrip("* ").strip()
                if len(clean) > 10 and not clean.startswith("#"):
                    mentions.append(clean)
    except Exception:
        pass
    return mentions


def scan_directory(dirpath, contact_name, first_word):
    """Scan all .md files in a directory for contact mentions."""
    results = {}  # filename -> [mentions]
    if not os.path.isdir(dirpath):
        return results
    for fname in os.listdir(dirpath):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(dirpath, fname)
        mentions = scan_file(fpath, contact_name, first_word)
        if mentions:
            results[fname] = mentions
    return results


def main():
    contacts, aliases = get_all_contacts()
    total_added = 0

    for contact in contacts:
        cid = contact["id"]
        name = contact["name"]
        first_word = name.split()[0]

        # Skip very short names that would match too broadly
        if len(first_word) < 3:
            continue

        existing = get_existing_interactions(cid)

        # Scan journal/
        journal_mentions = scan_directory(
            os.path.join(GOALS_DIR, "journal"), name, first_word
        )
        for fname, mentions in journal_mentions.items():
            date_str = fname.replace(".md", "")
            for m in mentions:
                summary = f"[journal {date_str}] {m[:200]}"
                if summary not in existing:
                    add_interaction(cid, "заметка", summary, source="daily-enrich")
                    existing.add(summary)
                    total_added += 1

        # Scan meetings/
        meeting_mentions = scan_directory(
            os.path.join(GOALS_DIR, "meetings"), name, first_word
        )
        for fname, mentions in meeting_mentions.items():
            for m in mentions:
                summary = f"[meeting {fname}] {m[:200]}"
                if summary not in existing:
                    add_interaction(cid, "встреча", summary, source="daily-enrich")
                    existing.add(summary)
                    total_added += 1

    print(f"CRM enrichment done: +{total_added} interactions from files")


if __name__ == "__main__":
    main()
