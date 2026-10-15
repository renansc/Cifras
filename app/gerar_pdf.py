#!/usr/bin/env python3
from pathlib import Path
import re, html as htmlmod
from bs4 import BeautifulSoup
from reportlab.platypus import BaseDocTemplate,Frame,PageTemplate,Paragraph,Spacer
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/'saida'; PDF=OUT/'pdf'; PDF.mkdir(parents=True,exist_ok=True)
for f in PDF.glob('*.pdf'):f.unlink()
def head(c,d,t):
 c.saveState();c.setFont('Helvetica-Bold',8);c.drawString(10*mm,202*mm,t[:115]);c.setFont('Helvetica',7);c.drawRightString(287*mm,202*mm,f'NanotechSoft-Cifras | {d.page}');c.restoreState()
def make(src,dst):
 soup=BeautifulSoup(src.read_text(encoding='utf-8',errors='ignore'),'html.parser'); cifra=soup.find(id='cifra')
 if not cifra:return False
 title=soup.title.get_text(' ',strip=True) if soup.title else src.stem; W,H=landscape(A4);m=10*mm;gap=7*mm;cw=(W-2*m-gap)/2
 frames=[Frame(m,10*mm,cw,H-24*mm,id='a'),Frame(m+cw+gap,10*mm,cw,H-24*mm,id='b')]
 doc=BaseDocTemplate(str(dst),pagesize=landscape(A4));doc.addPageTemplates(PageTemplate(id='two',frames=frames,onPage=lambda c,d:head(c,d,title)))
 normal=ParagraphStyle('n',fontName='Courier',fontSize=7.4,leading=8.8);chord=ParagraphStyle('c',parent=normal,fontName='Courier-Bold',textColor='#155aa8');hd=ParagraphStyle('h',fontName='Helvetica-Bold',fontSize=10,alignment=TA_CENTER,spaceAfter=4)
 story=[Paragraph(htmlmod.escape(title),hd)]; cre=re.compile(r'^\s*([A-G](?:#|b)?[^\s]*\s*)+$'); blank=0
 for line in cifra.get_text('\n').splitlines():
  line=line.rstrip()
  if not line.strip():
   blank+=1
   if blank<=1:story.append(Spacer(1,2.5))
   continue
  blank=0;safe=htmlmod.escape(line).replace(' ','&nbsp;');story.append(Paragraph(safe,chord if cre.match(line) and re.search(r'[A-G]',line) else normal))
 doc.build(story);return dst.exists() and dst.stat().st_size>500
files=[f for f in sorted(OUT.glob('*.html')) if re.match(r'^\d+_',f.name)];print('\n=== Exportando cifras para PDF (2 colunas) ===');ok=0
for f in files:
 d=PDF/(f.stem+'.pdf')
 try:
  if make(f,d):ok+=1;print('PDF OK:',d.name)
  else:print('PDF PENDENTE:',f.name)
 except Exception as e:print('PDF ERRO:',f.name,'-',e)
print(f'PDF: {ok}/{len(files)} gerados em {PDF}')
