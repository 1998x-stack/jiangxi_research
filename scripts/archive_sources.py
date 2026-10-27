"""Download cited pages without changing any research observations.

Run separately from prepare_data.py. A successful HTTP response is an archive,
not proof that every transcribed number in the page has been verified.
"""
from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ARCHIVE = DATA / "source_snapshots"
ARCHIVE.mkdir(parents=True, exist_ok=True)
headers = [
    "source_id", "retrieved_at_utc", "requested_url", "final_url", "http_status",
    "content_type", "path", "sha256", "bytes", "error",
]
sources = list(csv.DictReader((DATA / "sources.csv").open(encoding="utf-8-sig", newline="")))
records = []
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; academic source archiving)"})
for source in sources:
    record = {k: "" for k in headers}
    record["source_id"] = source["source_id"]
    record["requested_url"] = source["url"]
    record["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        response = session.get(source["url"], timeout=25)
        record["http_status"] = response.status_code
        record["final_url"] = response.url
        record["content_type"] = response.headers.get("Content-Type", "")
        response.raise_for_status()
        if not response.content:
            raise ValueError("empty response")
        suffix = ".pdf" if response.content.startswith(b"%PDF") else ".html"
        target = ARCHIVE / f"{source['source_id']}{suffix}"
        target.write_bytes(response.content)
        record["path"] = str(target.relative_to(ROOT))
        record["sha256"] = hashlib.sha256(response.content).hexdigest()
        record["bytes"] = len(response.content)
    except (requests.RequestException, ValueError) as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    records.append(record)
with (DATA / "source_snapshot_manifest.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
print(f"Archived {sum(bool(r['sha256']) for r in records)}/{len(records)} source responses")
