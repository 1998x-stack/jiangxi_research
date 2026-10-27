"""No-network tests of content-addressed source archiving."""
import hashlib
import importlib.util
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "source_archive", Path(__file__).with_name("archive_sources.py")
)
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)

with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    a,ha,sa = archive.archive_blob(root, "S99", b"<html>first edition</html>")
    again, hb, sb = archive.archive_blob(root, "S99", b"<html>first edition</html>")
    b,hc,sc = archive.archive_blob(root, "S99", b"<html>corrected edition</html>")
    assert a == again and ha == hb and sa == sb
    assert a != b and ha != hc
    assert (root/a).read_bytes() == b"<html>first edition</html>"
    assert (root/b).read_bytes() == b"<html>corrected edition</html>"
    assert hashlib.sha256((root/a).read_bytes()).hexdigest() == ha
    assert hashlib.sha256((root/b).read_bytes()).hexdigest() == hc
    assert sc == len(b"<html>corrected edition</html>")
    try:
        archive.archive_blob(root, "../escape", b"data")
        raise AssertionError("unsafe ID was accepted")
    except ValueError:
        pass
    c,hc,_ = archive.archive_blob(root, "S99", b"%PDF-1.7")
    assert c.endswith(".pdf")
print("PASS: immutable, content-addressed archival and unsafe-ID rejection")
