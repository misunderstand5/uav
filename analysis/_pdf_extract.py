"""Minimal PDF text extractor: decompress Flate streams and dump text operators."""
from __future__ import annotations
import re
import sys
import zlib
from pathlib import Path

pdf = Path(sys.argv[1]).read_bytes()
streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", pdf, flags=re.S)
print(f"# streams: {len(streams)}", file=sys.stderr)
out = []
for s in streams:
    try:
        data = zlib.decompress(s)
    except Exception:
        continue
    if b"Tj" not in data and b"TJ" not in data:
        continue
    # track text positions
    text = data.decode("latin-1", errors="ignore")
    # split by BT/ET blocks
    for block in re.findall(r"BT(.*?)ET", text, flags=re.S):
        # concatenate strings in order
        parts = []
        for m in re.finditer(r"\((?:\\.|[^\\()])*\)\s*Tj|\[(.*?)\]\s*TJ", block, flags=re.S):
            if m.group(0).endswith("Tj"):
                raw = re.match(r"\((.*)\)\s*Tj", m.group(0), flags=re.S).group(1)
                parts.append(raw)
            else:
                arr = m.group(1)
                for sm in re.finditer(r"\((?:\\.|[^\\()])*\)", arr, flags=re.S):
                    parts.append(sm.group(0)[1:-1])
        if parts:
            line = "".join(parts)
            line = line.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
            out.append(line)
result = "\n".join(out)
Path("analysis/_paper_extracted.txt").write_text(result, encoding="utf-8", errors="replace")
print(f"# chars: {len(result)}", file=sys.stderr)
