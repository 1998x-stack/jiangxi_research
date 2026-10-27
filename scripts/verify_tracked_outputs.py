"""Compare regenerated records to committed evidence independent of CSV BOM/newline differences."""
from pathlib import Path
import csv
import io
import json
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
    text = raw.decode('utf-8-sig')
    return list(csv.reader(io.StringIO(text, newline='')))

for rel in CSV_FILES:
    actual = (ROOT / rel).read_bytes()
    assert csv_records(committed_bytes(rel)) == csv_records(actual), f'CSV rows changed: {rel}'

for rel in JSON_FILES:
    actual = json.loads((ROOT / rel).read_text(encoding='utf-8-sig'))
    old = json.loads(committed_bytes(rel).decode('utf-8-sig'))
    assert old == actual, f'JSON metrics changed: {rel}'

for rel in TEXT_FILES:
    actual = (ROOT / rel).read_text(encoding='utf-8-sig').strip()
    old = committed_bytes(rel).decode('utf-8-sig').strip()
    assert old == actual, f'Text results changed: {rel}'

print('PASS: tracked CSV records, JSON metrics and validation summary match committed evidence')
