#!/usr/bin/env python3
"""Servidor local para controlar cifras na TV usando celular/PC na mesma rede."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json, secrets, socket, threading, time, argparse, hmac

ROOT = Path(__file__).resolve().parent
ROOM = str(secrets.randbelow(900000)+100000)
KEY = secrets.token_urlsafe(24)
LOCK = threading.Lock()
STATE = {"version":0,"song":None,"updated":None}

def default_backup():
    """Lê o backup da pasta principal; se houver vários, prefere o mais recente."""
    candidates=sorted(ROOT.glob("backup*.json"), key=lambda p:p.stat().st_mtime, reverse=True)
    for path in candidates:
        try:
            if path.stat().st_size>15*1024*1024:continue
            with path.open(encoding="utf-8") as fp: data=json.load(fp)
            if isinstance(data,dict) and data.get("version")==7 and isinstance(data.get("db"),dict) and data["db"].get("version")==7:
                return data
        except (OSError, ValueError, TypeError):pass
    return None

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        url=urlparse(self.path)
        if url.path in ("/controle", "/controle123"):
            page=(ROOT/"saida/NanotechSoft-Cifras.html").read_text(encoding="utf-8")
            page=page.replace("</head>","<script>window.NT_CONTROL_KEY="+json.dumps(KEY)+";</script></head>",1)
            # A base inicial é fornecida apenas pelo servidor. Não sobrescreve o navegador.
            backup=default_backup()
            if backup is not None:
                page=page.replace("</head>","<script>window.NT_INITIAL_BACKUP="+json.dumps(backup,ensure_ascii=False).replace("<", "\u003c")+";</script></head>",1)
            return self.send_html(page)
        if url.path in ("/tv", "/tv123"):
            page=(ROOT/"tv.html").read_text(encoding="utf-8")
            page=page.replace("</head>","<script>window.NT_ROOM="+json.dumps(ROOM)+";</script></head>",1)
            return self.send_html(page)
        if url.path=="/api/state":
            room=parse_qs(url.query).get("room",[""])[0]
            if not hmac.compare_digest(room,ROOM):return self.send_json({"error":"Sala inválida"},403)
            with LOCK:payload=dict(STATE)
            return self.send_json(payload)
        if url.path in ("/tv-antiga","/tv/"):
            self.path="/tv.html"
        elif url.path=="/":
            self.path="/saida/NanotechSoft-Cifras.html"
        else:
            self.path=url.path
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path!="/api/present":return self.send_json({"error":"Rota inválida"},404)
        if not hmac.compare_digest(self.headers.get("X-Controller-Key",""),KEY):
            return self.send_json({"error":"Acesso negado"},403)
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length<=0 or length>1024*1024:return self.send_json({"error":"Conteúdo excede o limite"},413)
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):raise ValueError("Objeto esperado")
            song={k:str(data.get(k,""))[:200000 if k in ("text","html") else 500] for k in ("title","artist","key","text","html")}
            try: song["fontSize"]=max(11,min(72,int(data.get("fontSize",24))))
            except (ValueError,TypeError): song["fontSize"]=24
            try: song["columns"]=max(1,min(3,int(data.get("columns",1))))
            except (ValueError,TypeError): song["columns"]=1
            song["dark"]=data.get("dark") is True
            with LOCK:
                STATE["version"]+=1;STATE["song"]=song;STATE["updated"]=time.time()
            return self.send_json({"ok":True,"version":STATE["version"]})
        except (ValueError,TypeError,json.JSONDecodeError):
            return self.send_json({"error":"JSON inválido"},400)
    def send_html(self,html):
        raw=html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def send_json(self,obj,status=200):
        raw=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def log_message(self,fmt,*args):
        super().log_message(fmt,*args)

def ip_lan():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("192.0.2.1",80));ip=s.getsockname()[0];s.close()
        return ip
    except OSError:return "IP_DO_COMPUTADOR"

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--port",type=int,default=8000)
    args=parser.parse_args()
    ip=ip_lan()
    print("\n=== NANOTECH CIFRAS | APRESENTAÇÃO EM DUAS TELAS ===",flush=True)
    print(f"CONTROLE (celular): http://{ip}:{args.port}/controle",flush=True)
    print(f"TELA (TV):          http://{ip}:{args.port}/tv",flush=True)
    print("Abra ambos na mesma rede Wi-Fi/LAN. Mantenha este servidor ligado.",flush=True)
    print("Use apenas em uma rede local confiável: os caminhos curtos não são senhas fortes.\n",flush=True)
    ThreadingHTTPServer(("0.0.0.0",args.port),Handler).serve_forever()
