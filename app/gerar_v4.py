#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
p=ROOT/"saida"/"NanotechSoft-Cifras.html"
if not p.exists():
    raise SystemExit("Execute primeiro app/gerar.py")

html=p.read_text(encoding="utf-8")
# Existing v3 contains const SONGS=[...]; reuse it as the seed database.
m=re.search(r'const SONGS=(\[.*?\]);\s*let current=',html,re.S)
if not m:
    raise SystemExit("Não foi possível localizar a biblioteca gerada.")
seed=m.group(1)
import json
seed_data=json.loads(seed)
existing={(str(x.get("num","")).zfill(2),x.get("song","").strip().lower()) for x in seed_data}
repfile=ROOT/"repertorio.txt"
if repfile.exists():
    for raw in repfile.read_text(encoding="utf-8").splitlines():
        raw=raw.strip()
        if not raw or raw.startswith("#"): continue
        parts=raw.split("|")
        while len(parts)<6: parts.append("")
        num,title,artist,key=parts[0].zfill(2),parts[1].strip(),parts[2].strip(),parts[3].strip()
        ident=(num,title.lower())
        if title and ident not in existing:
            seed_data.append({"num":num,"song":title,"artist":artist,"key":key,"html":"","pending":True})
            existing.add(ident)
seed=json.dumps(seed_data,ensure_ascii=False)

logo_match=re.search(r'<img src="(data:image/png;base64,[^"]+)" alt="NanotechSoft">',html)
logo=logo_match.group(1) if logo_match else ""

css=r'''*{box-sizing:border-box}html,body{margin:0;background:#101010;color:#fff;font-family:Arial}button,input,textarea{font:inherit}button{border:0;border-radius:8px;padding:9px;background:#3b3b3b;color:#fff;font-weight:bold}.top{position:sticky;top:0;z-index:20;background:#151515;padding:9px}.brand{display:flex;align-items:center;gap:9px}.brand img{width:44px;height:44px;object-fit:contain;background:#fff;border-radius:8px}.brand h1{margin:0;font-size:19px}.nav,.tools{display:flex;gap:5px;flex-wrap:wrap;margin-top:8px}.view{display:none;max-width:1050px;margin:auto;padding:9px}.view.on{display:block}.card{background:#222;border:1px solid #333;border-radius:9px;padding:10px;margin:7px 0}.row{display:flex;gap:8px;align-items:center}.grow{flex:1}.muted{color:#aaa;font-size:12px}.badge{background:#3a3a3a;padding:6px;border-radius:6px}.pending{color:#ffcc66;font-weight:bold;font-size:12px}.alias{color:#7ec8ff;font-size:12px;font-weight:bold}.field{width:100%;padding:9px;background:#202020;color:#fff;border:1px solid #555;border-radius:7px}.song{display:grid;grid-template-columns:1fr 55px auto;gap:7px;align-items:center}.actions{display:flex;gap:4px;flex-wrap:wrap}.actions button{font-size:11px;padding:7px}.modal{display:none;position:fixed;inset:0;background:#000c;z-index:100;align-items:center;justify-content:center;padding:10px}.modal.on{display:flex}.box{width:min(760px,100%);max-height:94vh;overflow:auto;background:#222;padding:13px;border-radius:10px}.box label{display:block;margin:8px 0 3px}.box textarea{min-height:330px;font-family:monospace}.checks{max-height:260px;overflow:auto;border:1px solid #444;padding:5px}.check{display:block;padding:6px;border-bottom:1px solid #333}
#stage{display:none;background:#fff;color:#000;min-height:100vh}#stage.dark{background:#111;color:#eee}#bar{position:sticky;top:0;background:#111;color:#fff;display:flex;gap:4px;align-items:center;padding:5px;z-index:30}#stitle{flex:1;text-align:center;font-weight:bold;font-size:12px}#chart{max-width:1050px;margin:auto;padding:10px;font:19px/1.55 monospace;column-count:1;column-gap:34px;column-rule:1px solid #bbb}.cols2{column-count:2!important;max-width:1500px!important}.cols3{column-count:3!important;max-width:1900px!important}.line,.chordline,.cifra-line,.note{break-inside:avoid-column}.chordline,.chord{color:#0561bd;font-weight:bold}.line,.chordline{white-space:pre-wrap;min-height:1.4em}.note{background:#fff1cc;color:#8a4200;border-left:5px solid #d97706;padding:5px;margin:7px 0;font-family:Arial;font-weight:bold}.dark .note{background:#3c2d00;color:#ffd166}.dark .chordline,.dark .chord{color:#64b5ff}.mark .line:hover,.mark .chordline:hover,.mark .cifra-line:hover{outline:2px dashed #d39e00}#float{display:none;position:fixed;right:4px;bottom:4px;background:#111;padding:4px;z-index:40;border-radius:7px}@media print{#bar,#float{display:none!important}#stage{display:block!important;background:#fff!important;color:#000!important}#chart{max-width:none!important;padding:0!important;font-size:11pt!important;column-gap:18pt;column-rule:.5pt solid #aaa}body{background:#fff!important}@page{size:A4 landscape;margin:10mm}}@media(max-width:600px){.song{grid-template-columns:1fr 45px}.song .actions{grid-column:1/-1}.nav button{flex:1;font-size:11px}#chart{font-size:16px}.brand h1{font-size:16px}}'''

manifest_path=ROOT/"repertorios_manifest.json"
manifest_json=manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else '{"repertoires":[],"songs":[]}'
js=r'''const SEED=__SEED__,MANIFEST=__MANIFEST__,K="nanotech_cifras_v7";let db,rep=null,sid=null,order=[],pos=-1,mark=false,fs=+(localStorage.palco_fonte||19),cols=+(localStorage.palco_colunas||1);
const $=x=>document.getElementById(x), esc=x=>{let d=document.createElement("div");d.textContent=x||"";return d.innerHTML}, uid=p=>p+"_"+Date.now().toString(36)+Math.random().toString(36).slice(2,6);
function fresh(){
 let byKey={};SEED.forEach(s=>byKey[(s.song||"").trim().toLowerCase()+"|"+(s.artist||"").trim().toLowerCase()]=s);
 let songs=(MANIFEST.songs||[]).map(m=>{let z=byKey[(m.title||"").trim().toLowerCase()+"|"+(m.artist||"").trim().toLowerCase()];return{id:m.id,title:m.title,artist:m.artist,key:m.key,html:z?z.html:"",text:null,pending:!(z&&z.html),observation:m.observation||""}});
 let reps=(MANIFEST.repertoires||[]).map(r=>({id:r.id,name:r.name,alias:r.alias||"",songs:r.songs||[]}));
 return{version:7,songs:songs.length?songs:SEED.map((s,i)=>({id:"seed_"+(i+1),title:s.song,artist:s.artist,key:s.key,html:s.html||"",pending:!!s.pending})),reps}
}
function load(){try{db=JSON.parse(localStorage.getItem(K))}catch(e){}if(!db||db.version!==7){db=fresh();if(!db.reps.length)db.reps=[{id:"principal",name:"Repertório Principal",alias:"",songs:db.songs.map(s=>s.id)}];save()}}
function save(){localStorage.setItem(K,JSON.stringify(db))}function song(id){return db.songs.find(x=>x.id===id)}function R(id){return db.reps.find(x=>x.id===id)}
function view(id){document.querySelectorAll(".view").forEach(x=>x.classList.remove("on"));$(id).classList.add("on");$("stage").style.display="none";$("shell").style.display="block";$("float").style.display="none"}
function reps(){let e=$("replist");e.innerHTML="";db.reps.forEach(r=>{let d=document.createElement("div");d.className="card row";d.innerHTML='<div class=grow><b>'+esc(r.name)+'</b>'+(r.alias?'<div class=alias>'+esc(r.alias)+'</div>':'')+'<div class=muted>'+r.songs.length+' músicas</div></div><div class=actions><button>ABRIR</button><button>EDITAR</button><button>EXCLUIR</button></div>';let b=d.querySelectorAll("button");b[0].onclick=()=>openrep(r.id);b[1].onclick=()=>editrep(r.id);b[2].onclick=()=>{if(confirm("Excluir repertório?")){db.reps=db.reps.filter(x=>x.id!==r.id);save();reps()}};e.appendChild(d)});view("reps")}
function library(){let q=$("libq").value.toLowerCase(),e=$("songs");e.innerHTML="";db.songs.filter(s=>(s.title+" "+s.artist+" "+s.key).toLowerCase().includes(q)).forEach(s=>{let d=document.createElement("div");d.className="card song";d.innerHTML='<div><b>'+esc(s.title)+'</b><div class=muted>'+esc(s.artist)+'</div>'+(s.pending?'<div class=pending>PENDENTE — use EDITAR para inserir a cifra</div>':'')+'</div><span class=badge>'+esc(s.key)+'</span><div class=actions><button>ABRIR</button><button>EDITAR</button><button>EXCLUIR</button></div>';let b=d.querySelectorAll("button");b[0].onclick=()=>stage(s.id,null);b[1].onclick=()=>editsong(s.id);b[2].onclick=()=>delsong(s.id);e.appendChild(d)});view("library")}
function newrep(){editrep(null)}function editrep(id){let r=id?R(id):{id:"",name:"",alias:"",songs:[]};$("rid").value=r.id;$("rname").value=r.name;$("ralias").value=r.alias||"";let c=$("checks");c.innerHTML="";db.songs.forEach(s=>{let l=document.createElement("label");l.className="check";l.innerHTML='<input type=checkbox value="'+s.id+'" '+(r.songs.includes(s.id)?"checked":"")+'> '+esc(s.title)+' — '+esc(s.artist);c.appendChild(l)});$("rmodal").classList.add("on")}
function saverep(){let id=$("rid").value,n=$("rname").value.trim(),alias=$("ralias").value.trim();if(!n)return alert("Informe o nome.");let songs=[...document.querySelectorAll("#checks input:checked")].map(x=>x.value);if(id){let r=R(id);r.name=n;r.alias=alias;r.songs=songs}else db.reps.push({id:uid("rep"),name:n,alias:alias,songs});save();closem("rmodal");reps()}
function openrep(id){rep=id;$("rtitle").textContent=R(id).name;drawrep();view("rep")}
function drawrep(){let r=R(rep),e=$("rsongs");e.innerHTML="";r.songs.forEach((id,i)=>{let s=song(id);if(!s)return;let d=document.createElement("div");d.className="card song";d.innerHTML='<div><b>'+(i+1)+'. '+esc(s.title)+'</b><div class=muted>'+esc(s.artist)+'</div>'+(s.pending?'<div class=pending>PENDENTE</div>':'')+'</div><span class=badge>'+esc(s.key)+'</span><div class=actions><button>ABRIR</button><button>↑</button><button>↓</button><button>REMOVER</button></div>';let b=d.querySelectorAll("button");b[0].onclick=()=>stage(id,rep);b[1].onclick=()=>move(i,-1);b[2].onclick=()=>move(i,1);b[3].onclick=()=>{r.songs=r.songs.filter(x=>x!==id);save();drawrep()};e.appendChild(d)})}
function move(i,n){let a=R(rep).songs,j=i+n;if(j<0||j>=a.length)return;[a[i],a[j]]=[a[j],a[i]];save();drawrep()}function addrep(){editrep(rep)}
function newsong(){editsong(null)}function textof(s){if(s.text!=null)return s.text;let d=document.createElement("div");d.innerHTML=s.html||"";return d.innerText||""}
function editsong(id){let s=id?song(id):{id:"",title:"",artist:"",key:"",text:""};$("sid").value=s.id;$("sname").value=s.title;$("sartist").value=s.artist;$("skey").value=s.key;$("stext").value=textof(s);$("smodal").classList.add("on")}
function savesong(){let id=$("sid").value,t=$("sname").value.trim();if(!t)return alert("Informe a música.");let txt=$("stext").value;let o={title:t,artist:$("sartist").value.trim(),key:$("skey").value.trim(),text:txt,html:"",pending:!txt.trim()};if(id)Object.assign(song(id),o);else db.songs.push({id:uid("song"),...o});save();closem("smodal");library()}
function delsong(id){if(!confirm("Excluir cifra da biblioteca e dos repertórios?"))return;db.songs=db.songs.filter(x=>x.id!==id);db.reps.forEach(r=>r.songs=r.songs.filter(x=>x!==id));save();library()}
function manual(t){return(t||"").split("\n").map(l=>{let ch=/^\s*([A-G](#|b)?[^\s]*\s*)+$/.test(l)&&/[A-G]/.test(l);return'<div class="'+(ch?"chordline":"line")+'">'+esc(l||" ")+"</div>"}).join("")}
function stage(id,rid){sid=id;rep=rid;order=rid?R(rid).songs.filter(song):db.songs.map(s=>s.id);pos=order.indexOf(id);let s=song(id);$("shell").style.display="none";$("stage").style.display="block";$("float").style.display="block";$("stitle").textContent=s.title+" — "+s.artist+" — "+s.key;$("chart").innerHTML=s.text!=null?manual(s.text):(s.html||"");$("chart").style.fontSize=fs+"px";applycols();[...$("chart").querySelectorAll(".line,.chordline,.cifra-line")].forEach((x,i)=>x.dataset.i=i);notes();scrollTo(0,0)}
function applycols(){let c=$("chart");c.classList.remove("cols2","cols3");if(cols===2)c.classList.add("cols2");if(cols===3)c.classList.add("cols3");let b=$("colbtn");if(b)b.textContent=cols+" COL"}function setcols(n){cols=n;localStorage.palco_colunas=n;applycols();scrollTo(0,0)}function cyclecols(){setcols(cols>=3?1:cols+1)}function exportpdf(){window.print()}function back(){rep?openrep(rep):library()}function prev(){if(pos>0)stage(order[pos-1],rep)}function next(){if(pos+1<order.length)stage(order[pos+1],rep)}
function nk(){return"nanotech_note_"+sid}function ng(){try{return JSON.parse(localStorage.getItem(nk())||"{}")}catch(e){return{}}}function notes(){let c=$("chart");c.querySelectorAll(".note").forEach(x=>x.remove());let n=ng();Object.keys(n).forEach(i=>{let l=c.querySelector('[data-i="'+i+'"]');if(!l)return;let d=document.createElement("div");d.className="note";d.textContent="✎ "+n[i];d.onclick=e=>{e.stopPropagation();editnote(i)};l.before(d)})}function editnote(i){let n=ng(),v=prompt("Anotação (vazio apaga):",n[i]||"");if(v===null)return;v=v.trim();v?n[i]=v:delete n[i];localStorage.setItem(nk(),JSON.stringify(n));notes()}$("chart").onclick=e=>{if(mark){let l=e.target.closest(".line,.chordline,.cifra-line");if(l)editnote(l.dataset.i)}};function annotate(){mark=!mark;$("chart").classList.toggle("mark",mark)}function plus(){fs=Math.min(36,fs+1);$("chart").style.fontSize=fs+"px";localStorage.palco_fonte=fs}function minus(){fs=Math.max(11,fs-1);$("chart").style.fontSize=fs+"px";localStorage.palco_fonte=fs}function theme(){$("stage").classList.toggle("dark");localStorage.palco_tema=$("stage").classList.contains("dark")?"dark":"light"}
function importtxt(){
 let inp=document.createElement("input");inp.type="file";inp.accept=".txt,text/plain";
 inp.onchange=()=>{let f=inp.files&&inp.files[0];if(!f)return;let rd=new FileReader();rd.onload=()=>{
  try{
   let lines=String(rd.result).split(/\r?\n/).map(x=>x.trim()).filter(x=>x&&!x.startsWith("#"));
   if(!lines.length)throw Error("TXT vazio.");
   let def=f.name.replace(/\.txt$/i,"").replace(/^repertorio[_ -]*/i,"").replace(/[_-]+/g," ").trim()||"Repertório importado";
   let name=prompt("Nome do novo repertório:",def);if(name===null)return;name=name.trim();if(!name)return;
   let alias=prompt("Apelido / nome da banda (opcional):","");if(alias===null)alias="";alias=alias.trim();
   let ids=[];
   lines.forEach(line=>{
    let p=line.split("|");while(p.length<5)p.push("");
    let num=(p[0]||"").trim(),title=(p[1]||"").trim(),artist=(p[2]||"").trim(),key=(p[3]||"").trim();
    let observation=(p[4]||"").trim();
    if(!title)return;
    let found=db.songs.find(s=>s.title.trim().toLowerCase()===title.toLowerCase()&&(s.artist||"").trim().toLowerCase()===artist.toLowerCase());
    if(!found){found={id:uid("song"),title,artist,key,text:"",html:"",pending:true,observation,num};db.songs.push(found)}
    else {if(!found.key&&key)found.key=key;if(observation)found.observation=observation}
    ids.push(found.id)
   });
   db.reps.push({id:uid("rep"),name,alias,songs:[...new Set(ids)]});save();reps();
   alert('Repertório "'+name+'" importado com '+ids.length+' músicas. As cifras novas entram como PENDENTE; use EDITAR para preenchê-las.');
  }catch(e){alert("Erro ao importar: "+e.message)}
 };rd.readAsText(f)};inp.click()
}
function backup(){let n={};for(let i=0;i<localStorage.length;i++){let k=localStorage.key(i);if(k&&k.startsWith("nanotech_note_"))n[k]=localStorage.getItem(k)}let x={app:"NanotechSoft-Cifras",version:7,date:new Date().toISOString(),db,notes:n,settings:{font:localStorage.palco_fonte||"19",theme:localStorage.palco_tema||"light"}},b=new Blob([JSON.stringify(x,null,2)],{type:"application/json"}),a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="backup_NanotechSoft-Cifras_v4.json";a.click()}
function restore(){let i=document.createElement("input");i.type="file";i.accept=".json";i.onchange=()=>{let r=new FileReader();r.onload=()=>{try{let x=JSON.parse(r.result);if(x.version!==7||!x.db)throw Error("Backup incompatível");db=x.db;save();Object.keys(x.notes||{}).forEach(k=>localStorage.setItem(k,x.notes[k]));if(x.settings){localStorage.palco_fonte=x.settings.font||"19";localStorage.palco_tema=x.settings.theme||"light"}reps();alert("Backup restaurado.")}catch(e){alert(e.message)}};r.readAsText(i.files[0])};i.click()}function closem(id){$(id).classList.remove("on")}load();setTimeout(applycols,0);if(localStorage.palco_tema==="dark")$("stage").classList.add("dark");reps();'''

js=js.replace("__SEED__",seed).replace("__MANIFEST__",manifest_json)
doc='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NanotechSoft-Cifras</title><style>'+css+'</style></head><body><div id="shell"><div class="top"><div class="brand"><img src="'+logo+'"><div><h1>NanotechSoft-Cifras</h1><div class="muted">Biblioteca e repertórios offline</div></div></div><div class="nav"><button onclick="reps()">REPERTÓRIOS</button><button onclick="library()">TODAS AS CIFRAS</button><button onclick="newsong()">+ NOVA CIFRA</button><button onclick="newrep()">+ NOVO REPERTÓRIO</button><button onclick="backup()">BACKUP</button><button onclick="restore()">RESTAURAR</button><button onclick="importtxt()">IMPORTAR TXT</button></div></div><section id="reps" class="view"><div class="tools"><h2 class="grow">Repertórios</h2><button onclick="newrep()">+ NOVO</button></div><div id="replist"></div></section><section id="library" class="view"><h2>Todas as Cifras</h2><div class="tools"><input class="field" id="libq" placeholder="Buscar..." oninput="library()"><button onclick="newsong()">+ NOVA</button></div><div id="songs"></div></section><section id="rep" class="view"><div class="tools"><button onclick="reps()">← REPERTÓRIOS</button><h2 class="grow" id="rtitle"></h2><button onclick="addrep()">+ MÚSICAS</button></div><div id="rsongs"></div></section></div><div id="stage"><div id="bar"><button onclick="prev()">← ANTERIOR</button><button onclick="back()">VOLTAR</button><div id="stitle"></div><button onclick="next()">PRÓXIMA →</button></div><div id="chart"></div></div><div id="float"><button onclick="minus()">A−</button><button onclick="plus()">A+</button><button id="colbtn" onclick="cyclecols()">1 COL</button><button onclick="setcols(1)">1</button><button onclick="setcols(2)">2</button><button onclick="setcols(3)">3</button><button onclick="theme()">CLARO/ESCURO</button><button onclick="annotate()">ANOTAR</button><button onclick="exportpdf()">PDF</button></div><div id="smodal" class="modal"><div class="box"><h2>Cifra</h2><input id="sid" type="hidden"><label>Música</label><input id="sname" class="field"><label>Artista</label><input id="sartist" class="field"><label>Tom</label><input id="skey" class="field"><label>Cifra / letra</label><textarea id="stext" class="field"></textarea><div class="tools"><button onclick="savesong()">SALVAR</button><button onclick="closem(\'smodal\')">CANCELAR</button></div></div></div><div id="rmodal" class="modal"><div class="box"><h2>Repertório</h2><input id="rid" type="hidden"><label>Nome</label><input id="rname" class="field" placeholder="Ex.: Rock"><label>Apelido / Banda</label><input id="ralias" class="field" placeholder="Ex.: Banda X"><label>Músicas</label><div id="checks" class="checks"></div><div class="tools"><button onclick="saverep()">SALVAR</button><button onclick="closem(\'rmodal\')">CANCELAR</button></div></div></div><script>'+js+'</script></body></html>'
p.write_text(doc,encoding="utf-8")
print("V4 criada:",p)
