import pathlib

p = pathlib.Path("analysis/fig2_publication.html")
s = p.read_text(encoding="utf-8")
s = s.replace(r"\n  .flowlegend", "\n  .flowlegend")
p.write_text(s, encoding="utf-8")
print("ok")
