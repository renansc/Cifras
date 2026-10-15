#!/usr/bin/env python3
from pathlib import Path
base=Path(__file__).resolve().parent.parent
p=base/'saida'/'NanotechSoft-Cifras.html'
s=p.read_text(encoding='utf-8')
if 'id="nt-app-menu"' not in s:
    css=(base/'app/menu3d.css').read_text()
    html=(base/'app/menu3d.html').read_text()
    js=(base/'app/menu3d.js').read_text()
    s=s.replace('</style>',css+'</style>',1)
    s=s.replace('<div id="bar"><button','<div id="bar"><button onclick="ntMenu(\'main\')">⌂ MENU 3D</button><button',1)
    s=s.replace('<div id="stage">',html+'<div id="stage">',1)
    s=s.replace('</body>','<script>'+js+'</script><script>window.addEventListener("load",()=>ntMenu("main"));</script></body>',1)
    p.write_text(s,encoding='utf-8')
print('Menu 3D aplicado.')
