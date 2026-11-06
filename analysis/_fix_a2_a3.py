import pathlib

p = pathlib.Path("analysis/fig2_publication.html")
s = p.read_text(encoding="utf-8")
s = s.replace(
    '<p>QoS classes<br><span class="eq">R<sub>i</sub><sup>min</sup> ∈ {0.7, 2.0, 2.5}</span> Mbit/s</p>',
    '<p><b>QoS</b> 0.7 / 2 / 2.5</p>\n        <p class="small">Mbit/s per class</p>',
)
s = s.replace(
    '<text x="38" y="56" font-family="Arial" font-size="5.2" fill="#5a6570" text-anchor="middle">M-UAVs</text>',
    "",
)
p.write_text(s, encoding="utf-8")
print("ok")
