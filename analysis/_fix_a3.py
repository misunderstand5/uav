import pathlib

p = pathlib.Path("analysis/fig2_publication.html")
s = p.read_text(encoding="utf-8")
start = s.index('<svg class="assoc"')
end = s.index("</svg>", start) + len("</svg>")
new = '''<div class="assoc-row">
        <svg viewBox="0 0 118 58" xmlns="http://www.w3.org/2000/svg">
          <g fill="none" stroke="#0f6b5c" stroke-width="0.9">
            <circle cx="13" cy="15" r="8" opacity="0.55"/>
            <circle cx="13" cy="43" r="8" opacity="0.35"/>
            <circle cx="44" cy="29" r="8" opacity="0.55"/>
            <line x1="21" y1="17" x2="36" y2="26"/>
            <line x1="21" y1="41" x2="36" y2="32"/>
          </g>
          <g fill="#0f6b5c"><circle cx="13" cy="15" r="2.0"/><circle cx="13" cy="43" r="2.0"/><circle cx="44" cy="29" r="2.0"/></g>
          <text x="44" y="56" font-family="Arial" font-size="5.2" fill="#5a6570" text-anchor="middle">GU clusters</text>
        </svg>
        <span class="arr">→</span>
        <svg viewBox="0 0 86 58" xmlns="http://www.w3.org/2000/svg">
          <g transform="translate(2,6)">
            <use href="#uav" x="0" y="0" width="22" height="22"/>
            <use href="#uav" x="26" y="0" width="22" height="22"/>
            <use href="#uav" x="0" y="26" width="22" height="22"/>
            <use href="#uav" x="26" y="26" width="22" height="22"/>
          </g>
          <text x="38" y="56" font-family="Arial" font-size="5.2" fill="#5a6570" text-anchor="middle">M-UAVs</text>
        </svg>
      </div>'''
s = s[:start] + new + s[end:]
s = s.replace(
    ".a3 .assoc { position: absolute; left: 0.05in; bottom: 0.12in; width: 1.92in; height: 0.55in; }",
    ".a3 .assoc-row { display: flex; align-items: center; gap: 0.04in; margin-top: 0.04in; height: 0.58in; }\n"
    "  .a3 .assoc-row svg { height: 0.56in; width: auto; }\n"
    "  .a3 .assoc-row .arr { font-size: 8pt; color: #0f6b5c; }",
)
p.write_text(s, encoding="utf-8")
print("ok")
