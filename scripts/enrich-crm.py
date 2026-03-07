#!/usr/bin/env python3
"""Daily CRM enrichment: scan journal/, meetings/ for new mentions of contacts.
Uses a single DB connection for speed."""
import os
import sys
from datetime import datetime, timezone, timedelta

GOALS_DIR = os.path.expanduser("~/goals")
BOT_DIR = os.path.expanduser("~/telegram-backlog-bot")
sys.path.insert(0, BOT_DIR)

# Resolve DATABASE_URL
DATABASE_URL = os.environ.get("CRM_DATABASE_URL") or os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    env_path = os.path.join(BOT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    DATABASE_URL = line.strip().split("=", 1)[1]
                    break
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:TIKpyViTcgQVrhscBSOEnrUyDwoAUePR@shortline.proxy.rlwy.net:28452/railway"
os.environ["DATABASE_URL"] = DATABASE_URL

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("psycopg2 not available, skipping")
    sys.exit(0)

MOSCOW_TZ = timezone(timedelta(hours=3))
TODAY = datetime.now(MOSCOW_TZ).date()


def scan_dir(dirpath):
    """Read all .md files in a directory. Returns {filename: content}."""
    result = {}
    if not os.path.isdir(dirpath):
        return result
    for fname in os.listdir(dirpath):
        if not fname.endswith(".md"):
            continue
        try:
            with open(os.path.join(dirpath, fname), "r") as f:
                result[fname] = f.read()
        except Exception:
            pass
    return result


def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Load all contacts
    cur.execute("SELECT id, name FROM contacts ORDER BY id")
    contacts = cur.fetchall()

    # Load all existing interaction summaries (one query)
    cur.execute("SELECT contact_id, summary FROM interactions")
    existing = {}
    for r in cur.fetchall():
        existing.setdefault(r["contact_id"], set()).add(r["summary"])

    # Pre-read all files
    journal_files = scan_dir(os.path.join(GOALS_DIR, "journal"))
    meeting_files = scan_dir(os.path.join(GOALS_DIR, "meetings"))

    total_added = 0

    for contact in contacts:
        cid = contact["id"]
        name = contact["name"]
        first_word = name.split()[0]

        if len(first_word) < 3:
            continue

        contact_existing = existing.get(cid, set())
        fw_lower = first_word.lower()

        # Scan journal
        for fname, content in journal_files.items():
            if fw_lower not in content.lower():
                continue
            date_str = fname.replace(".md", "")
            for line in content.split("\n"):
                if fw_lower not in line.lower() or not line.strip():
                    continue
                clean = line.strip().lstrip("- ").lstrip("* ").strip()
                if len(clean) <= 10 or clean.startswith("#"):
                    continue
                summary = f"[journal {date_str}] {clean[:200]}"
                if summary not in contact_existing:
                    cur.execute(
                        "INSERT INTO interactions (contact_id, type, date, summary, source) VALUES (%s, %s, %s, %s, %s)",
                        (cid, "заметка", TODAY, summary, "daily-enrich")
                    )
                    contact_existing.add(summary)
                    total_added += 1

        # Scan meetings
        for fname, content in meeting_files.items():
            if fw_lower not in content.lower():
                continue
            for line in content.split("\n"):
                if fw_lower not in line.lower() or not line.strip():
                    continue
                clean = line.strip().lstrip("- ").lstrip("* ").strip()
                if len(clean) <= 10 or clean.startswith("#"):
                    continue
                summary = f"[meeting {fname}] {clean[:200]}"
                if summary not in contact_existing:
                    cur.execute(
                        "INSERT INTO interactions (contact_id, type, date, summary, source) VALUES (%s, %s, %s, %s, %s)",
                        (cid, "встреча", TODAY, summary, "daily-enrich")
                    )
                    contact_existing.add(summary)
                    total_added += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"CRM enrichment done: +{total_added} interactions from files")


if __name__ == "__main__":
    main()
