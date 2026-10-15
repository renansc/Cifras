#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
import html,re,unicodedata

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"saida"; ORIG=ROOT/"originais"
OUT.mkdir(exist_ok=True); ORIG.mkdir(exist_ok=True)

LOGO_FILE = ROOT/"assets"/"nanotechsoft-logo.png"
LOGO_DATA = ""
if LOGO_FILE.exists():
    import base64
    LOGO_DATA = "data:image/png;base64," + base64.b64encode(LOGO_FILE.read_bytes()).decode("ascii")

def slug(s):
    s=unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+","_",s).strip("_").lower()

def read_items():
    result=[]
    for line in (ROOT/"repertorio.txt").read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        p=line.split("|")
        while len(p)<6: p.append("")
        try: steps=int(p[5].strip() or 0)
        except ValueError: steps=0
        result.append({"num":p[0].zfill(2),"song":p[1].strip(),"artist":p[2].strip(),
                       "key":p[3].strip(),"url":p[4].strip(),"steps":steps})
    return result

sharp=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
flat=["C","Db","D","Eb","E","F","Gb","G","Ab","A","Bb","B"]
vals={"C":0,"C#":1,"Db":1,"D":2,"D#":3,"Eb":3,"E":4,"F":5,"F#":6,"Gb":6,
      "G":7,"G#":8,"Ab":8,"A":9,"A#":10,"Bb":10,"B":11}
rx=re.compile(r"^([A-G](?:#|b)?)(.*)$")

def trans_one(x,steps):
    m=rx.match(x)
    if not m: return x
    root=m.group(1); arr=flat if "b" in root else sharp
    return arr[(vals[root]+steps)%12]+m.group(2)

def trans_chord(c,steps):
    p=c.split("/",1)
    return trans_one(p[0],steps)+("/"+trans_one(p[1],steps) if len(p)>1 else "")

CSS = r'''*{box-sizing:border-box}html,body{margin:0;background:#fff;color:#000}body{font-family:Arial;padding-top:62px}
#nav{position:fixed;top:0;left:0;right:0;min-height:55px;background:#111;display:flex;align-items:center;justify-content:space-between;padding:5px 9px;z-index:9999}
#nav a{color:#fff;text-decoration:none;font-weight:bold;font-size:12px}#cifra{max-width:1050px;margin:auto;padding:12px;font-family:monospace;font-size:19px;line-height:1.55}
.chord{font-weight:bold!important;color:#0561bd!important}#ctl{position:fixed;right:5px;bottom:5px;background:#111;padding:5px;border-radius:8px;z-index:9999}
#ctl button{background:#333;color:#fff;border:0;border-radius:5px;padding:7px;margin:1px;font-weight:bold}.note{margin:9px 0 2px;padding:5px 9px;background:#fff1cc;color:#8a4200;border-left:5px solid #d97706;font-family:Arial;font-weight:bold;cursor:pointer}
.dark,.dark #cifra{background:#111!important;color:#eee!important}.dark .chord{color:#64b5ff!important}.dark .note{background:#3c2d00;color:#ffd166}.mark .cifra-line:hover{background:#fff3cd;outline:2px dashed #d39e00}
@media(max-width:600px){#cifra{font-size:16px;padding:7px}#nav a{font-size:9px}#ctl button{font-size:10px;padding:6px}}'''

JS = r'''(()=>{let c=document.querySelector("#cifra");if(!c)return;let p=location.pathname.split("/").pop(),kn="palco_notas_"+p,L=[...c.querySelectorAll(".cifra-line")],mark=false,fs=+(localStorage.palco_fonte||19);
L.forEach((x,i)=>x.dataset.i=i);let get=()=>{try{return JSON.parse(localStorage.getItem(kn)||"{}")}catch(e){return{}}},save=n=>localStorage.setItem(kn,JSON.stringify(n));
let edit=i=>{let n=get(),v=prompt("Anotação (vazio apaga):",n[i]||"");if(v===null)return;v=v.trim();v?n[i]=v:delete n[i];save(n);render()};
let render=()=>{c.querySelectorAll(".note").forEach(x=>x.remove());let n=get();Object.keys(n).forEach(i=>{let l=c.querySelector('[data-i="'+i+'"]');if(!l)return;let d=document.createElement("div");d.className="note";d.textContent="✎ "+n[i];d.onclick=e=>{e.stopPropagation();edit(i)};l.before(d)})};
window.plus=()=>{fs=Math.min(36,fs+1);c.style.fontSize=fs+"px";localStorage.palco_fonte=fs};window.minus=()=>{fs=Math.max(11,fs-1);c.style.fontSize=fs+"px";localStorage.palco_fonte=fs};c.style.fontSize=fs+"px";
if(localStorage.palco_tema==="dark")document.body.classList.add("dark");window.theme=()=>{document.body.classList.toggle("dark");localStorage.palco_tema=document.body.classList.contains("dark")?"dark":"light"};
window.annot=()=>{mark=!mark;document.body.classList.toggle("mark",mark)};c.onclick=e=>{if(!mark)return;let l=e.target.closest(".cifra-line");if(l)edit(l.dataset.i)};
window.expnotes=()=>{let d={};for(let i=0;i<localStorage.length;i++){let k=localStorage.key(i);if(k&&k.startsWith("palco_notas_"))d[k]=localStorage.getItem(k)}let b=new Blob([JSON.stringify(d,null,2)],{type:"application/json"}),a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="anotacoes_app_cifra.json";a.click()};
window.impnotes=()=>{let i=document.createElement("input");i.type="file";i.accept=".json";i.onchange=()=>{let r=new FileReader();r.onload=()=>{try{let d=JSON.parse(r.result);Object.keys(d).forEach(k=>{if(k.startsWith("palco_notas_"))localStorage.setItem(k,d[k])});render();alert("Notas importadas")}catch(e){alert("Arquivo inválido")}};r.readAsText(i.files[0])};i.click()};render()})()'''

items=read_items()
for p in OUT.glob("*.html"): p.unlink()
downloaded=[]

for x in items:
    if not x["url"]:
        print("["+x["num"]+"] PENDENTE: sem URL")
        continue
    name=f'{x["num"]}_{slug(x["song"])}_{x["key"]}.html'
    src=ORIG/name
    try:
        req=Request(x["url"],headers={"User-Agent":"Mozilla/5.0"})
        src.write_bytes(urlopen(req,timeout=25).read())
        soup=BeautifulSoup(src.read_text(encoding="utf-8",errors="ignore"),"html.parser")
        cifra=soup.find(id="cifra")
        if not cifra: raise RuntimeError("#cifra não encontrado")
        for q in cifra.find_all(["script","iframe","img","picture","video","svg","canvas","form","button"]): q.decompose()
        for e in cifra.select(".chord"):
            old=e.get("data-original") or e.get_text(strip=True)
            new=trans_chord(old,x["steps"])
            e.string=new; e["data-original"]=new
        downloaded.append((x,name,cifra))
        print("["+x["num"]+"] OK")
    except Exception as exc:
        print("["+x["num"]+"] PENDENTE:",exc)

for i,(x,name,cifra) in enumerate(downloaded):
    prev=downloaded[i-1][1] if i else None
    nxt=downloaded[i+1][1] if i+1<len(downloaded) else None
    left=f'<a href="{prev}">← ANTERIOR</a>' if prev else "<span></span>"
    right=f'<a href="{nxt}">PRÓXIMA →</a>' if nxt else "<span></span>"
    title=html.escape(f'NanotechSoft-Cifras — {x["num"]} — {x["song"]} — {x["key"]}')
    ctl='<div id="ctl"><button onclick="minus()">A−</button><button onclick="plus()">A+</button><button onclick="theme()">☀/🌙</button><button onclick="annot()">✎ ANOTAR</button><button onclick="expnotes()">⇩ NOTAS</button><button onclick="impnotes()">⇧ NOTAS</button></div>'
    doc='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><style>'+CSS+'</style></head><body><div id="nav">'+left+'<a href="index.html">☰ '+title+'</a>'+right+'</div>'+str(cifra)+ctl+'<script>'+JS+'</script></body></html>'
    (OUT/name).write_text(doc,encoding="utf-8")

available={x["num"]:name for x,name,_ in downloaded}
rows=[]
for x in items:
    if x["num"] in available:
        action='<a href="'+available[x["num"]]+'">ABRIR</a>'; cls="m"
    else:
        action="<span>PENDENTE</span>"; cls="m pend"
    rows.append('<div class="'+cls+'"><b>'+x["num"]+'</b><div><strong>'+html.escape(x["song"])+'</strong><small>'+html.escape(x["artist"])+'</small></div><em>'+html.escape(x["key"])+'</em>'+action+'</div>')

ICSS='body{margin:0;background:#111;color:#fff;font-family:Arial}header{position:sticky;top:0;background:#181818;padding:12px;z-index:5}h2{margin:0 0 10px}.toolbar{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:10px}.toolbar button{border:0;border-radius:7px;background:#444;color:#fff;padding:10px 12px;font-weight:bold;cursor:pointer}.toolbar button:hover{background:#666}input[type=search]{width:100%;box-sizing:border-box;padding:11px;font-size:17px;background:#292929;color:#fff;border:1px solid #555;border-radius:7px}.list{padding:9px}.m{display:grid;grid-template-columns:35px 1fr 55px 70px;gap:7px;align-items:center;background:#222;padding:10px;margin:7px 0;border-radius:8px}.m small{display:block;color:#aaa;margin-top:3px}.m em{font-style:normal;font-weight:bold}.m a{color:#fff;background:#555;padding:7px;text-decoration:none;border-radius:5px}.pend{opacity:.45}#status{font-size:13px;color:#bbb;margin-top:8px}@media(max-width:600px){.toolbar button{flex:1;padding:10px 5px;font-size:12px}.m{grid-template-columns:28px 1fr 45px 60px;font-size:13px}}'

BACKUP_JS = r"""
function filterList(){
  let q=document.querySelector("#q").value.toLowerCase();
  document.querySelectorAll(".m").forEach(x=>{
    x.style.display=x.innerText.toLowerCase().includes(q)?"grid":"none";
  });
}

function setStatus(msg){
  let s=document.getElementById("status");
  if(s) s.textContent=msg;
}

function criarBackup(){
  let anotacoes={};
  for(let i=0;i<localStorage.length;i++){
    let k=localStorage.key(i);
    if(k && k.startsWith("palco_notas_")){
      try { anotacoes[k.substring("palco_notas_".length)] = JSON.parse(localStorage.getItem(k)||"{}"); }
      catch(e){ anotacoes[k.substring("palco_notas_".length)] = {}; }
    }
  }

  let backup={
    app:"app_cifra",
    versao:2,
    data:new Date().toISOString(),
    configuracoes:{
      fonte:localStorage.getItem("palco_fonte") || "19",
      tema:localStorage.getItem("palco_tema") || "light"
    },
    anotacoes:anotacoes
  };

  let blob=new Blob([JSON.stringify(backup,null,2)],{type:"application/json"});
  let a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  let agora=new Date();
  let nome="backup_app_cifra_"+agora.getFullYear()+"-"+String(agora.getMonth()+1).padStart(2,"0")+"-"+String(agora.getDate()).padStart(2,"0")+".json";
  a.download=nome;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href),1000);
  setStatus("Backup criado: "+nome);
}

function restaurarBackup(){
  let inp=document.createElement("input");
  inp.type="file";
  inp.accept=".json,application/json";
  inp.onchange=()=>{
    let f=inp.files && inp.files[0];
    if(!f) return;
    let r=new FileReader();
    r.onload=()=>{
      try{
        let b=JSON.parse(r.result);
        if(b.app!=="app_cifra" || !b.anotacoes) throw new Error("Backup incompatível");

        if(b.configuracoes){
          if(b.configuracoes.fonte!=null) localStorage.setItem("palco_fonte",String(b.configuracoes.fonte));
          if(b.configuracoes.tema!=null) localStorage.setItem("palco_tema",String(b.configuracoes.tema));
        }

        Object.keys(b.anotacoes).forEach(nome=>{
          localStorage.setItem("palco_notas_"+nome,JSON.stringify(b.anotacoes[nome]||{}));
        });

        setStatus("Backup restaurado com sucesso. Abra uma música para conferir.");
        alert("Backup restaurado com sucesso.");
      }catch(e){
        alert("Não foi possível restaurar: "+e.message);
      }
    };
    r.readAsText(f);
  };
  inp.click();
}

function limparAnotacoes(){
  if(!confirm("Apagar TODAS as anotações deste navegador? Faça um backup antes se quiser recuperá-las.")) return;
  let apagar=[];
  for(let i=0;i<localStorage.length;i++){
    let k=localStorage.key(i);
    if(k && k.startsWith("palco_notas_")) apagar.push(k);
  }
  apagar.forEach(k=>localStorage.removeItem(k));
  setStatus(apagar.length+" conjunto(s) de anotações removido(s).");
}
"""

toolbar = '<div class="toolbar"><button onclick="criarBackup()">💾 BACKUP</button><button onclick="restaurarBackup()">♻ RESTAURAR</button><button onclick="limparAnotacoes()">🗑 LIMPAR NOTAS</button></div>'
index_doc='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NanotechSoft-Cifras</title><style>'+ICSS+'</style></head><body><header><div style="display:flex;align-items:center;gap:10px"><img src="'+LOGO_DATA+'" alt="NanotechSoft" style="width:44px;height:44px;object-fit:contain;background:#fff;border-radius:9px;padding:3px"><h2>NanotechSoft-Cifras</h2></div>'+toolbar+'<input type="search" id="q" placeholder="Buscar música, artista ou tom..." oninput="filterList()"><div id="status">Backup inclui anotações, tema e tamanho da fonte.</div></header><div class="list">'+''.join(rows)+'</div><script>'+BACKUP_JS+'</script></body></html>'
(OUT/"index.html").write_text(index_doc,encoding="utf-8")
print("Disponíveis:",len(downloaded),"/",len(items))
print("Índice v2: Backup / Restaurar / Limpar notas habilitados.")


# ============================================================
# V3: ARQUIVO ÚNICO PARA DRIVE / TABLET
# ============================================================
single_songs=[]
for x,name,cifra in downloaded:
    single_songs.append({
        "num": x["num"],
        "song": x["song"],
        "artist": x["artist"],
        "key": x["key"],
        "html": str(cifra)
    })

import json
songs_json=json.dumps(single_songs,ensure_ascii=False)

SINGLE_CSS=r"""
*{box-sizing:border-box}html,body{margin:0;background:#111;color:#fff;font-family:Arial,sans-serif}
body.light{background:#f5f5f5;color:#111}
#top{position:sticky;top:0;z-index:1000;background:#151515;padding:8px;box-shadow:0 2px 8px #0008}
.brand{display:flex;align-items:center;gap:10px}.brand img{width:46px;height:46px;object-fit:contain;background:#fff;border-radius:9px;padding:3px}
.brand h1{font-size:19px;margin:0}.brand small{display:block;color:#aaa;margin-top:2px}
#homeTools{display:flex;gap:5px;flex-wrap:wrap;margin-top:8px}
button,#search{border:0;border-radius:7px;padding:9px;font-weight:bold}
button{background:#3b3b3b;color:#fff;cursor:pointer}button:hover{background:#555}
#search{flex:1;min-width:180px;background:#292929;color:#fff;border:1px solid #555}
#list{padding:8px}.row{display:grid;grid-template-columns:34px 1fr 52px 64px;gap:6px;align-items:center;background:#222;padding:10px;margin:7px 0;border-radius:8px}
.row small{display:block;color:#aaa;margin-top:3px}.row .key{font-weight:bold}.row button{padding:7px}
#viewer{display:none;background:#fff;color:#000;min-height:100vh}
#viewer.dark{background:#111;color:#eee}
#songbar{position:sticky;top:0;z-index:900;background:#111;color:#fff;display:flex;align-items:center;justify-content:space-between;gap:4px;padding:6px}
#songbar button{padding:8px 7px;font-size:12px}
#songTitle{text-align:center;font-weight:bold;font-size:13px;flex:1}
#cifraWrap{max-width:1050px;margin:auto;padding:12px;font-family:monospace;font-size:19px;line-height:1.55}
#cifraWrap .chord{font-weight:bold!important;color:#0561bd!important}
#viewer.dark #cifraWrap .chord{color:#64b5ff!important}
.note{margin:9px 0 2px;padding:5px 9px;background:#fff1cc;color:#8a4200;border-left:5px solid #d97706;font-family:Arial;font-weight:bold;cursor:pointer}
#viewer.dark .note{background:#3c2d00;color:#ffd166}.mark .cifra-line:hover{background:#fff3cd;outline:2px dashed #d39e00}
#float{position:fixed;right:5px;bottom:5px;background:#111;padding:4px;border-radius:8px;z-index:1200;display:none}
#float button{font-size:11px;padding:7px 6px}
@media(max-width:600px){.brand h1{font-size:17px}.row{grid-template-columns:28px 1fr 42px 55px;font-size:13px}#cifraWrap{font-size:16px;padding:7px}#songbar button{font-size:10px;padding:7px 5px}}
"""

SINGLE_JS=r"""
const SONGS=__SONGS__;
let current=-1,mark=false,fs=+(localStorage.palco_fonte||19);
const list=document.getElementById("list"),home=document.getElementById("home"),viewer=document.getElementById("viewer"),wrap=document.getElementById("cifraWrap"),float=document.getElementById("float");

function noteKey(){return current<0?"":("palco_notas_single_"+SONGS[current].num)}
function getNotes(){try{return JSON.parse(localStorage.getItem(noteKey())||"{}")}catch(e){return{}}}
function saveNotes(n){localStorage.setItem(noteKey(),JSON.stringify(n))}
function prepLines(){[...wrap.querySelectorAll(".cifra-line")].forEach((x,i)=>x.dataset.i=i)}
function renderNotes(){
 wrap.querySelectorAll(".note").forEach(x=>x.remove());let n=getNotes();
 Object.keys(n).forEach(i=>{let l=wrap.querySelector('[data-i="'+i+'"]');if(!l)return;let d=document.createElement("div");d.className="note";d.textContent="✎ "+n[i];d.onclick=e=>{e.stopPropagation();editNote(i)};l.before(d)})
}
function editNote(i){let n=getNotes(),v=prompt("Anotação (vazio apaga):",n[i]||"");if(v===null)return;v=v.trim();v?n[i]=v:delete n[i];saveNotes(n);renderNotes()}
function openSong(i){
 current=i;home.style.display="none";viewer.style.display="block";float.style.display="block";
 document.getElementById("songTitle").textContent=SONGS[i].num+" — "+SONGS[i].song+" — "+SONGS[i].key;
 wrap.innerHTML=SONGS[i].html;wrap.style.fontSize=fs+"px";prepLines();renderNotes();window.scrollTo(0,0);
}
function closeSong(){viewer.style.display="none";float.style.display="none";home.style.display="block";current=-1;window.scrollTo(0,0)}
function prevSong(){if(current>0)openSong(current-1)}
function nextSong(){if(current>=0&&current<SONGS.length-1)openSong(current+1)}
function plus(){fs=Math.min(36,fs+1);wrap.style.fontSize=fs+"px";localStorage.palco_fonte=fs}
function minus(){fs=Math.max(11,fs-1);wrap.style.fontSize=fs+"px";localStorage.palco_fonte=fs}
function theme(){viewer.classList.toggle("dark");localStorage.palco_tema=viewer.classList.contains("dark")?"dark":"light"}
function annot(){mark=!mark;wrap.classList.toggle("mark",mark)}
wrap.onclick=e=>{if(!mark)return;let l=e.target.closest(".cifra-line");if(l)editNote(l.dataset.i)}

function drawList(q=""){
 list.innerHTML="";
 SONGS.forEach((s,i)=>{
  let txt=(s.num+" "+s.song+" "+s.artist+" "+s.key).toLowerCase();if(!txt.includes(q.toLowerCase()))return;
  let d=document.createElement("div");d.className="row";
  d.innerHTML="<b>"+s.num+"</b><div><strong>"+esc(s.song)+"</strong><small>"+esc(s.artist)+"</small></div><div class=key>"+esc(s.key)+"</div><button>ABRIR</button>";
  d.querySelector("button").onclick=()=>openSong(i);list.appendChild(d);
 })
}
function esc(x){let d=document.createElement("div");d.textContent=x;return d.innerHTML}
document.getElementById("search").oninput=e=>drawList(e.target.value);

function backup(){
 let notes={};
 for(let i=0;i<localStorage.length;i++){let k=localStorage.key(i);if(k&&(k.startsWith("palco_notas_single_")||k.startsWith("palco_notas_")))notes[k]=localStorage.getItem(k)}
 let b={app:"NanotechSoft-Cifras",versao:3,data:new Date().toISOString(),configuracoes:{fonte:localStorage.palco_fonte||"19",tema:localStorage.palco_tema||"light"},storage:notes};
 let blob=new Blob([JSON.stringify(b,null,2)],{type:"application/json"}),a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="backup_NanotechSoft-Cifras.json";a.click()
}
function restore(){
 let i=document.createElement("input");i.type="file";i.accept=".json";i.onchange=()=>{let r=new FileReader();r.onload=()=>{try{let b=JSON.parse(r.result);if(!b.storage)throw Error("backup incompatível");Object.keys(b.storage).forEach(k=>localStorage.setItem(k,b.storage[k]));if(b.configuracoes){if(b.configuracoes.fonte)localStorage.palco_fonte=b.configuracoes.fonte;if(b.configuracoes.tema)localStorage.palco_tema=b.configuracoes.tema}alert("Backup restaurado.")}catch(e){alert("Erro: "+e.message)}};r.readAsText(i.files[0])};i.click()
}
if(localStorage.palco_tema==="dark")viewer.classList.add("dark");
drawList();
"""

single_js=SINGLE_JS.replace("__SONGS__",songs_json)
logo_html=LOGO_DATA
single_doc='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NanotechSoft-Cifras</title><style>'+SINGLE_CSS+'</style></head><body><div id="home"><div id="top"><div class="brand"><img src="'+logo_html+'" alt="NanotechSoft"><div><h1>NanotechSoft-Cifras</h1><small>Repertório offline</small></div></div><div id="homeTools"><input id="search" placeholder="Buscar música, artista ou tom..."><button onclick="backup()">💾 BACKUP</button><button onclick="restore()">♻ RESTAURAR</button></div></div><div id="list"></div></div><div id="viewer"><div id="songbar"><button onclick="prevSong()">← ANTERIOR</button><button onclick="closeSong()">☰ REPERTÓRIO</button><div id="songTitle"></div><button onclick="nextSong()">PRÓXIMA →</button></div><div id="cifraWrap"></div></div><div id="float"><button onclick="minus()">A−</button><button onclick="plus()">A+</button><button onclick="theme()">☀/🌙</button><button onclick="annot()">✎ ANOTAR</button></div><script>'+single_js+'</script></body></html>'

(OUT/"NanotechSoft-Cifras.html").write_text(single_doc,encoding="utf-8")
print("Arquivo único:",OUT/"NanotechSoft-Cifras.html")
