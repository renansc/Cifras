#!/usr/bin/env python3
from pathlib import Path
import subprocess, shutil, json, re, sys, urllib.parse, urllib.request, html

ROOT=Path(__file__).resolve().parent.parent
REP_DIR=ROOT/"repertorios"
LEGACY=ROOT/"app"/"gerar.py"
MAIN=ROOT/"repertorio.txt"
OUT=ROOT/"saida"
OUT.mkdir(exist_ok=True)

def meta(path):
    name=path.stem.replace("_"," ").replace("-"," ").title()
    alias=""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# NOME:"): name=line.split(":",1)[1].strip() or name
        elif line.startswith("# APELIDO:"): alias=line.split(":",1)[1].strip()
    return name,alias

def rows(path):
    out=[]
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw=raw.strip()
        if not raw or raw.startswith("#"): continue
        p=raw.split("|")
        while len(p)<7:p.append("")
        # Supports old 5-col observation and standard 6/7-col source format.
        num,title,artist,key=p[0].strip(),p[1].strip(),p[2].strip(),p[3].strip()
        url=p[4].strip() if len(p)>=6 and p[4].strip().startswith(("http://","https://")) else ""
        semi=p[5].strip() if url else "0"
        obs=p[6].strip() if url else (p[4].strip() if len(p)>4 else "")
        out.append(dict(num=num.zfill(2),title=title,artist=artist,key=key,url=url,semitones=semi or "0",observation=obs))
    return out

def norm(s):
    import unicodedata
    s=unicodedata.normalize("NFKD",s)
    s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+"," ",s.lower()).strip()

def fetch(url, timeout=15):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/154 Safari/537.36","Accept-Language":"pt-BR,pt;q=0.9,en;q=0.7"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.geturl(),r.read().decode("utf-8","ignore")

def search_cifranet(title, artist):
    # Pesquisa pública oficial do CifraNET.
    queries=[f"{title} {artist}", title]
    nt,na=norm(title),norm(artist)
    for q in queries:
        search_url="https://www.cifranet.com.br/pesquisa.php?"+urllib.parse.urlencode({"q":q})
        try:
            _,body=fetch(search_url)
        except Exception as e:
            print("  pesquisa.php falhou:",type(e).__name__)
            continue
        hrefs=re.findall(r'href\s*=\s*["\x27]([^"\x27]*/cifra/[^"\x27]+)["\x27]',body,re.I)
        candidates=[]
        for h in hrefs:
            h=html.unescape(h)
            if h.startswith("//"): h="https:"+h
            elif h.startswith("/"): h="https://www.cifranet.com.br"+h
            elif not h.startswith("http"): h=urllib.parse.urljoin("https://www.cifranet.com.br/",h)
            if "cifranet.com.br/cifra/" in h:
                candidates.append(h.split("#",1)[0].split("?",1)[0])

        def score(u):
            nu=norm(urllib.parse.unquote(u))
            return sum(5 for w in nt.split() if len(w)>1 and w in nu)+sum(2 for w in na.split() if len(w)>1 and w in nu)

        for u in sorted(set(candidates),key=score,reverse=True):
            nu=norm(urllib.parse.unquote(u))
            tw=[w for w in nt.split() if len(w)>2]
            aw=[w for w in na.split() if len(w)>2]
            if tw and not all(w in nu for w in tw): continue
            if aw and not any(w in nu for w in aw): continue
            try:
                final,page=fetch(u)
            except Exception:
                continue
            plain=norm(re.sub(r"<[^>]+>"," ",page[:180000]))
            title_ok=(not tw or all(w in plain for w in tw))
            artist_ok=(not aw or any(w in plain for w in aw))
            low=page.lower()
            cifra_ok=("/cifra/" in final and ("id=\"cifra\"" in low or "class=\"chord\"" in low or "cifra de " in low))
            if title_ok and artist_ok and cifra_ok:
                return final
    return ""

files=sorted(REP_DIR.glob("*.txt"))
if not files:
    raise SystemExit("Nenhum TXT em repertorios/")

manifest={"repertoires":[],"songs":[]}
songmap={}
all_rows=[]
for rf in files:
    name,alias=meta(rf); ids=[]
    for row in rows(rf):
        sk=(row["title"].casefold(),row["artist"].casefold())
        if sk not in songmap:
            sid="m"+str(len(songmap)+1).zfill(4); songmap[sk]=sid
            item=dict(row); item["id"]=sid; manifest["songs"].append(item)
        sid=songmap[sk]; ids.append(sid)
        # Prefer source URL if a later repertoire supplies one.
        item=next(x for x in manifest["songs"] if x["id"]==sid)
        if not item.get("url") and row.get("url"):
            item.update(url=row["url"],semitones=row["semitones"])
    manifest["repertoires"].append({"id":"rep_"+rf.stem,"name":name,"alias":alias,"songs":ids})

# Resolve missing sources automatically before invoking the legacy downloader.
print("\\n=== Procurando fontes ausentes no CifraNET ===")
for x in manifest["songs"]:
    if not x.get("url"):
        print("BUSCA:",x["title"],"-",x["artist"],"-> pesquisa.php")
        found=search_cifranet(x["title"],x["artist"])
        if found:
            x["url"]=found; print("  OK:",found)
        else: print("  PENDENTE: fonte não encontrada automaticamente")
(ROOT/"repertorios_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")

# Build one combined legacy input so each unique URL is downloaded once.
lines=["# Numero|Musica|Artista|Tom|URL|Semitons"]
for i,x in enumerate(manifest["songs"],1):
    lines.append("|".join([str(i).zfill(2),x["title"],x["artist"],x["key"],x.get("url",""),x.get("semitones","0")]))
MAIN.write_text("\n".join(lines)+"\n",encoding="utf-8")
(ROOT/"repertorios_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")

subprocess.run([sys.executable,str(LEGACY)],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(ROOT/"app"/"gerar_v4.py")],cwd=ROOT,check=True)
print("\\nOK: processados",len(files),"repertórios e",len(manifest["songs"]),"músicas.")
