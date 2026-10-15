#!/usr/bin/env python3
from pathlib import Path
base=Path(__file__).resolve().parent.parent
p=base/'saida/NanotechSoft-Cifras.html'
s=p.read_text(encoding='utf-8')
old='function load(){try{db=JSON.parse(localStorage.getItem(K))}catch(e){}if(!db||db.version!==7){db=fresh();if(!db.reps.length)db.reps=[{id:"principal",name:"Repertório Principal",alias:"",songs:db.songs.map(s=>s.id)}];save()}}'
new='function load(){\n try{db=JSON.parse(localStorage.getItem(K))}catch(e){}\n if(!db||db.version!==7){\n  const backup=window.NT_INITIAL_BACKUP;\n  if(backup&&backup.version===7&&backup.db&&backup.db.version===7){\n   db=backup.db;\n   try{Object.entries(backup.notes||{}).forEach(([k,v])=>{if(k.startsWith("nanotech_note_"))localStorage.setItem(k,v)})}catch(e){}\n   try{if(backup.settings){if(backup.settings.font)localStorage.palco_fonte=backup.settings.font;if(backup.settings.theme)localStorage.palco_tema=backup.settings.theme}}catch(e){}\n   window.NT_INITIAL_BACKUP=null;\n  }else{db=fresh()}\n  if(!db.reps.length)db.reps=[{id:"principal",name:"Repertório Principal",alias:"",songs:db.songs.map(s=>s.id)}];\n  save();\n }\n}'
if old in s:
    s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')
print('V16: restauração inicial configurada')
