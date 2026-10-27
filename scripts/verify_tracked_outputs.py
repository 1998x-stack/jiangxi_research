"""Compare generated scientific records with committed outputs; tolerate only floating-point roundoff."""
from pathlib import Path
import csv
import io
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parent.parent
CSV_FILES = [
    'data/sources.csv',
    'data/observations_reviewed.csv',
    'data/regions_2025.csv',
    'outputs/ganzhou_population_2024_2025.csv',
]
JSON_FILES = ['outputs/analysis_results.json']
TEXT_FILES = ['outputs/validation_summary.txt']

def committed_bytes(path):
    return subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT)

def csv_records(raw):
    return list(csv.reader(io.StringIO(raw.decode('utf-8-sig'), newline='')))

def close(a, b):
    if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
        return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-9)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(close(x,y) for x,y in zip(a,b))
    return a == b

for rel in CSV_FILES:
    actual = (ROOT / rel).read_bytes()
    assert csv_records(committed_bytes(rel)) == csv_records(actual), f'CSV rows changed: {rel}'

for rel in JSON_FILES:
    actual = json.loads((ROOT / rel).read_text(encoding='utf-8-sig'))
    old = json.loads(committed_bytes(rel).decode('utf-8-sig'))
    assert close(old, actual), f'JSON metrics changed beyond floating-point roundoff: {rel}'

for rel in TEXT_FILES:
    actual = (ROOT / rel).read_text(encoding='utf-8-sig').strip()
    old = committed_bytes(rel).decode('utf-8-sig').strip()
    assert old == actual, f'Text results changed: {rel}'

print('PASS: tracked CSV records, numerically equivalent JSON and validation summary')
