#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
p = root / "saida/NanotechSoft-Cifras.html"
s = p.read_text(encoding="utf-8")
js = (root / "app/transposicao.js").read_text(encoding="utf-8")

# A chamada ntTransposeRender no palco não significa que a implementação foi incluída.
marker = "/* NANOTECH_TRANSPOSICAO_EMBUTIDA */"
if marker not in s:
    script = "<script>\n" + marker + "\n" + js + "\n</script>"
    s = s.replace("</body>", script + "</body>", 1)
    if marker not in s:
        raise RuntimeError("Não foi possível incluir a transposição no HTML")
    p.write_text(s, encoding="utf-8")
print("Transposição instalada e verificada.")
