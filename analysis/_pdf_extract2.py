"""Position-aware PDF text extraction (enough for a LaTeX paper)."""
from __future__ import annotations
import re
import sys
import zlib
from pathlib import Path

pdf = Path(sys.argv[1]).read_bytes()
streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", pdf, flags=re.S)

TOKEN = re.compile(
    rb"\((?:\\\\.|[^\\\\()])*\)"          # string
    rb"|\[[^\]]*\]"                       # array
    rb"|[-+]?\d*\.?\d+"                   # number
    rb"|/[^\s/\[\]()<>]+"                 # name
    rb"|[A-Za-z][A-Za-z0-9*'\"]*"         # operator/name
    rb"|<<|>>"                            # dict delimiters
)

def decode_string(raw: bytes) -> str:
    s = raw[1:-1]
    s = re.sub(rb"\\([nrtbf()\\])", lambda m: {b"n": b"\n", b"r": b"\r", b"t": b"\t",
                                               b"b": b"\b", b"f": b"\f",
                                               b"(": b"(", b")": b")", b"\\": b"\\"}[m.group(1)], s)
    s = re.sub(rb"\\([0-7]{1,3})", lambda m: bytes([int(m.group(1), 8)]), s)
    return s.decode("latin-1", errors="ignore")

def char_width(ch: str, fs: float) -> float:
    if ch == " ":
        return 0.25 * fs
    if ch in "il.,:;'|!":
        return 0.28 * fs
    if ch in "mwMW@%":
        return 0.85 * fs
    if ch.isupper():
        return 0.62 * fs
    return 0.50 * fs

out_lines = []
last_end_x = None
last_y = None
buf: list[str] = []
for s in streams:
    try:
        data = zlib.decompress(s)
    except Exception:
        continue
    if b"Tj" not in data and b"TJ" not in data:
        continue
    text = data.decode("latin-1", errors="ignore")
    for block in re.findall(r"BT(.*?)ET", text, flags=re.S):
        block_b = block.encode("latin-1", errors="ignore")
        tokens = [m.group(0) for m in TOKEN.finditer(block_b)]
        stack: list = []
        # text state
        x = y = 0.0
        line_x = line_y = 0.0
        fs = 10.0
        leading = 12.0
        last_end_x = None
        last_y = None
        buf = []
        def emit(txt: str, nx: float, ny: float, fs_: float):
            global last_end_x, last_y, buf
            if not txt:
                return
            if last_y is not None and abs(ny - last_y) > 0.6 * fs_:
                if buf:
                    out_lines.append("".join(buf))
                    buf = []
            elif last_end_x is not None and nx - last_end_x > 0.22 * fs_:
                if buf and not buf[-1].endswith(" "):
                    buf.append(" ")
            buf.append(txt)
            last_end_x = nx + sum(char_width(c, fs_) for c in txt)
            last_y = ny
        for tok in tokens:
            if tok.startswith(b"("):
                stack.append(("str", decode_string(tok)))
            elif tok.startswith(b"["):
                items = re.findall(rb"\((?:\\\\.|[^\\\\()])*\)|[-+]?\d*\.?\d+", tok)
                arr = []
                for it in items:
                    if it.startswith(b"("):
                        arr.append(("s", decode_string(it)))
                    else:
                        arr.append(("n", float(it)))
                stack.append(("arr", arr))
            elif re.fullmatch(rb"[-+]?\d*\.?\d+", tok):
                stack.append(("num", float(tok)))
            elif tok.startswith(b"/"):
                stack.append(("name", tok.decode("latin-1")))
            else:
                op = tok.decode("latin-1")
                if op == "Tm" and len(stack) >= 6:
                    nums = [v for k, v in stack[-6:] if k == "num"]
                    if len(nums) == 6:
                        x = nums[4]; y = nums[5]; line_x = x; line_y = y
                elif op in ("Td", "TD") and len(stack) >= 2:
                    nums = [v for k, v in stack[-2:] if k == "num"]
                    if len(nums) == 2:
                        line_x += nums[0]; line_y += nums[1]
                        x = line_x; y = line_y
                        if op == "TD":
                            leading = -nums[1]
                elif op == "T*":
                    line_y -= leading if leading else 1.2 * fs
                    x = line_x; y = line_y
                elif op == "Tf" and len(stack) >= 2:
                    nums = [v for k, v in stack[-2:] if k == "num"]
                    if nums:
                        fs = nums[0]
                elif op in ("Tj", "'", '"') and stack and stack[-1][0] == "str":
                    txt = stack[-1][1]
                    emit(txt, x, y, fs)
                    x += sum(char_width(c, fs) for c in txt)
                elif op == "TJ" and stack and stack[-1][0] == "arr":
                    for kind, val in stack[-1][1]:
                        if kind == "s":
                            emit(val, x, y, fs)
                            x += sum(char_width(c, fs) for c in val)
                        else:
                            x += -val / 1000.0 * fs
                stack = []
        if buf:
            out_lines.append("".join(buf))

result = "\n".join(out_lines)
Path("analysis/_paper_positioned.txt").write_text(result, encoding="utf-8", errors="replace")
print(f"# chars: {len(result)} lines: {len(out_lines)}", file=sys.stderr)
