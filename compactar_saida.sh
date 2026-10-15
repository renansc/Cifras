#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -f NanotechSoft-Cifras_completo.zip NanotechSoft-Cifras_unico.zip
python3 - <<'PY'
from pathlib import Path
import zipfile
out=Path("saida")
with zipfile.ZipFile("NanotechSoft-Cifras_completo.zip","w",zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.glob("*.html")):
        z.write(p,Path("NanotechSoft-Cifras")/p.name)
with zipfile.ZipFile("NanotechSoft-Cifras_unico.zip","w",zipfile.ZIP_DEFLATED) as z:
    p=out/"NanotechSoft-Cifras.html"
    if p.exists(): z.write(p,p.name)
print("CRIADOS:")
print(" - NanotechSoft-Cifras_completo.zip")
print(" - NanotechSoft-Cifras_unico.zip")
PY
