#!/usr/bin/env python3
from pathlib import Path
base=Path(__file__).resolve().parent.parent
p=base/'saida/NanotechSoft-Cifras.html'
s=p.read_text(encoding='utf-8')
if 'ntPresentationEnabled' not in s:
    js=(base/'app/aplicar_v14.js').read_text(encoding='utf-8')
    s=s.replace('</body>','<script>'+js+'</script></body>',1)
    p.write_text(s,encoding='utf-8')
print('V14: integração aplicada')
