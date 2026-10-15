#!/usr/bin/env python3
from pathlib import Path
base=Path(__file__).resolve().parent.parent
p=base/'saida'/'NanotechSoft-Cifras.html'
s=p.read_text(encoding='utf-8')
css=Path(__file__).with_name('carrossel_giratorio.css').read_text(encoding='utf-8')
html=Path(__file__).with_name('carrossel_giratorio.html').read_text(encoding='utf-8')
js=Path(__file__).with_name('carrossel_giratorio.js').read_text(encoding='utf-8')
if 'id="nt-wheel"' not in s:
 s=s.replace('</style>',css+'</style>',1)
 s=s.replace('<div id="stage">',html+'<div id="stage">',1)
 s=s.replace('function prev(){if(pos>0)stage(order[pos-1],rep)}function next(){if(pos+1<order.length)stage(order[pos+1],rep)}','function prev(){wheelShow(-1)}function next(){wheelShow(1)}',1)
 s=s.replace('<div id="bar"><button','<div id="bar"><button onclick="wheelShow(0)">◉ CARROSSEL 3D</button><button',1)
 s=s.replace('</body>','<script>'+js+'</script></body>',1)
 p.write_text(s,encoding='utf-8')
print('Carrossel giratório integrado em:',p)
