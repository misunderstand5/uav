import pathlib

p = pathlib.Path("analysis/fig2_publication.html")
s = p.read_text(encoding="utf-8")
s = s.replace(
    ".flowlegend { position: absolute; left: 2.36in; top: 4.14in; width: 4.62in; font-size: 5.6pt; color: var(--muted); }",
    ".flowlegend { position: absolute; left: 2.32in; top: 1.84in; width: 4.62in; font-size: 5.8pt; color: var(--muted); }",
)
s = s.replace(
    '<text x="44" y="56" font-family="Arial" font-size="5.2" fill="#5a6570" text-anchor="middle">GU clusters</text>',
    "",
)
p.write_text(s, encoding="utf-8")
print("ok")
