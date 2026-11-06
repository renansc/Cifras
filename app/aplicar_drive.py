#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'saida/NanotechSoft-Cifras.html'
s=p.read_text(encoding='utf-8')
def replace_one(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError('marcador ausente ou duplicado: '+a[:60])
 s=s.replace(a,b,1)
replace_one('<button onclick="backup()">BACKUP</button>','<button onclick="atualizarDrive()">ATUALIZAR</button><button onclick="backup()">BACKUP</button>')
replace_one(" {name:'BACKUP',desc:"," {name:'ATUALIZAR',desc:'Atualizar cifras do Google Drive.',icon:'⟳',kind:'update'},\n {name:'BACKUP',desc:")
replace_one(" case 'backup':backup();break;"," case 'update':atualizarDrive();break;\n case 'backup':backup();break;")
replace_one('function restore(){',"""async function atualizarDrive(){
 try{
  const url=new URL('../dados_cifras.json',window.location.href).href;
  const response=await fetch(url+'&_='+Date.now(),{cache:'no-store'});
  if(!response.ok)throw new Error('HTTP '+response.status);
  const x=await response.json();
  if(x.version!==7||!x.db||x.db.version!==7||!Array.isArray(x.db.songs)||!Array.isArray(x.db.reps))throw new Error('Backup v7 inválido');
  if(!confirm('Atualizar com a cópia publicada do Drive substituirá os dados locais. Faça BACKUP antes de confirmar. Continuar?'))return;
  const old=db;db=x.db;
  try{save()}catch(e){db=old;throw e}
  const ids=new Set(db.songs.map(x=>String(x.id)));
  for(let i=localStorage.length-1;i>=0;i--){let k=localStorage.key(i);if(k&&k.startsWith('nanotech_note_'))localStorage.removeItem(k)}
  for(const [k,v] of Object.entries(x.notes||{}))if(k.startsWith('nanotech_note_')&&ids.has(k.slice(14)))localStorage.setItem(k,v);
  selectedSongIds.clear();selectedRepIds.clear();reps();alert('Dados atualizados da cópia publicada do Drive.');
 }catch(e){alert('Não foi possível atualizar pelo Google Drive: '+e.message+'. Dados locais preservados.')}
}
function restore(){""")
p.write_text(s,encoding='utf-8')
print('Botão Atualizar Drive incorporado ao HTML final.')
