#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'saida/NanotechSoft-Cifras.html'
s=p.read_text(encoding='utf-8')
def replace_one(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError('marcador ausente ou duplicado: '+a[:60])
 s=s.replace(a,b,1)
replace_one('<button onclick="backup()">BACKUP</button>','<button onclick="atualizarDrive()">ATUALIZAR</button><button onclick="backup()">BACKUP</button>')
replace_one(" {name:'BACKUP',desc:"," {name:'ATUALIZAR',desc:'Atualizar cifras do JSON do GitHub.',icon:'⟳',kind:'update'},\n {name:'BACKUP',desc:")
replace_one(" case 'backup':backup();break;"," case 'update':atualizarDrive();break;\n case 'backup':backup();break;")
replace_one('function restore(){',"""const NT_DATA_URL=new URL('../Dados_App_Cifras.json',window.location.href).href;
const NT_SYNC_KEY='nt_github_backup_last_applied_v1';
async function atualizarDrive(silent=false){
 try{
  const response=await fetch(NT_DATA_URL+'?t='+Date.now(),{cache:'no-store'});
  if(!response.ok)throw new Error('HTTP '+response.status);
  const x=await response.json();
  if(x.app!=='NanotechSoft-Cifras'||x.version!==7||!x.db||x.db.version!==7||!Array.isArray(x.db.songs)||!Array.isArray(x.db.reps))throw new Error('Backup v7 inválido');
  const fingerprint=JSON.stringify(x.db);
  const existing=localStorage.getItem(K);
  const last=localStorage.getItem(NT_SYNC_KEY);
  if(existing&&existing===fingerprint){
   localStorage.setItem(NT_SYNC_KEY,fingerprint);
   if(!silent)alert('O repertório já está atualizado.');
   return;
  }
  if(existing&&last!==existing){
   if(!silent&&!confirm('Existem dados locais possivelmente diferentes. Salve um BACKUP antes de substituir. Continuar?'))return;
  }
  if(!silent&&existing&&last===existing&&!confirm('Substituir os dados locais pelo JSON mais recente do GitHub?'))return;
  if(silent&&existing&&existing!==fingerprint){try{localStorage.setItem('nt_backup_antes_sync_'+Date.now(),existing)}catch(e){console.warn('Não foi possível guardar cópia local antes da sincronização',e)}}
  const old=db;db=x.db;
  try{save()}catch(e){db=old;throw e}
  const ids=new Set(db.songs.map(item=>String(item.id)));
  for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k&&k.startsWith('nanotech_note_'))localStorage.removeItem(k);}
  for(const [k,v] of Object.entries(x.notes||{}))if(k.startsWith('nanotech_note_')&&ids.has(k.slice(14)))localStorage.setItem(k,v);
  if(x.settings){
   if(x.settings.font)localStorage.palco_fonte=x.settings.font;
   if(x.settings.theme)localStorage.palco_tema=x.settings.theme;
  }
  localStorage.setItem(NT_SYNC_KEY,JSON.stringify(db));
  selectedSongIds.clear();selectedRepIds.clear();reps();
  if(!silent)alert('Repertório atualizado pelo GitHub.');
 }catch(e){
  if(!silent)alert('Falha ao consultar o JSON do GitHub: '+e.message+'. Dados locais preservados.');
  else console.warn('Falha na atualização do GitHub',e);
 }
}
function restore(){""")
replace_one('reps();</script><script>','reps();atualizarDrive(true);</script><script>')
# Registro do service worker no escopo raiz, válido também na rota /saida/.
replace_one('</head>', '''<link rel="manifest" href="/Cifras/manifest.webmanifest">
<meta name="theme-color" content="#202020">
<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') {
 window.addEventListener('load', () => navigator.serviceWorker.register('/Cifras/sw.js', {scope:'/Cifras/'}).catch(e => console.warn('Offline indisponível:', e)));
}
</script>
</head>''')
p.write_text(s,encoding='utf-8')
print('Botão Atualizar Drive incorporado ao HTML final.')
