"""Versioned archiving of registered research source responses.

HTTP fetches are an *explicit* manual operation, never part of offline CI.
A successful downloaded page does not validate any number's statistical meaning.
Snapshots are immutable and content-addressed; repeated downloads never overwrite
existing evidence bytes. Failed requests do not erase the last successful manifest.
"""
from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ARCHIVE = DATA / "source_snapshots"
MANIFEST = DATA / "source_snapshot_manifest.csv"
HISTORY = DATA / "source_snapshot_history.csv"

FIELDS = (
    "source_id", "retrieved_at_utc", "requested_url", "final_url", "http_status",
    "content_type", "path", "sha256", "bytes", "error",
)

def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

def archive_blob(root: Path, source_id: str, blob: bytes) -> tuple[str, str, int]:
    """Store bytes at a new SHA-256 address; never replace existing bytes."""
    if not source_id or "/" in source_id or "\\" in source_id or source_id in {".", ".."}:
        raise ValueError("unsafe source_id")
    if not blob:
        raise ValueError("empty downloaded response")
    digest = hashlib.sha256(blob).hexdigest()
    suffix = ".pdf" if blob.startswith(b"%PDF") else ".html"
    rel = Path("data") / "source_snapshots" / source_id / f"{digest}{suffix}"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as stream:
            stream.write(blob)
    except FileExistsError:
        # Refuse to proceed if an on-disk object has been modified or corrupted.
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("previously archived content-addressed snapshot was altered")
    return rel.as_posix(), digest, len(blob)

def archive_all() -> None:
    import requests  # Only necessary for explicitly requested network refreshes.

    sources = read_csv(DATA / "sources.csv")
    previous = {r["source_id"]: r for r in read_csv(MANIFEST)}
    attempts = read_csv(HISTORY)
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; academic source archiving)"})
    latest = []
    successes = 0

    for source in sources:
        sid = source["source_id"]
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        attempt = {k: "" for k in FIELDS}
        attempt.update({"source_id": sid, "requested_url": source["url"], "retrieved_at_utc": now})
        try:
            response = session.get(source["url"], timeout=25)
            attempt.update({
                "http_status": str(response.status_code),
                "final_url": response.url,
                "content_type": response.headers.get("Content-Type", ""),
            })
            response.raise_for_status()
            rel, digest, size = archive_blob(ROOT, sid, response.content)
            attempt.update({"path": rel, "sha256": digest, "bytes": str(size)})
            latest.append(attempt)
            successes += 1
        except (requests.RequestException, ValueError, OSError) as exc:
            attempt["error"] = f"{type(exc).__name__}: {exc}"
            # Retain last known good version; log failed refresh separately.
            latest.append(previous.get(sid, attempt))
        attempts.append(attempt)

    write_csv(MANIFEST, latest)
    write_csv(HISTORY, attempts)
    print(f"Successfully refreshed {successes}/{len(sources)}; preserved previous versions on failure")

if __name__ == "__main__":
    archive_all()
