#!/usr/bin/env python3
from pathlib import Path
base=Path(__file__).resolve().parent.parent
p=base/'saida/NanotechSoft-Cifras.html'
s=p.read_text(encoding='utf-8')
old=(base/'app/aplicar_v14.js').read_text(encoding='utf-8')
if 'window.NT_CONTROL_KEY' not in s:
    # Replaces previous V14 inline script after generator has inserted it
    start=s.find('/* Correções V14:')
    if start!=-1:
        end=s.find('</script>',start)
        if end!=-1:s=s[:start]+old+s[end:]
    p.write_text(s,encoding='utf-8')
print('V15 aplicada')
