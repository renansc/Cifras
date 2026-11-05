#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=root/"saida/NanotechSoft-Cifras.html"
s=p.read_text(encoding="utf-8")
js=(root/"app/transposicao.js").read_text(encoding="utf-8")
if "ntTransposeRender" not in s:
    s=s.replace("</body>","<script>"+js+"</script></body>",1)
    p.write_text(s,encoding="utf-8")
print("Transposição instalada.")
