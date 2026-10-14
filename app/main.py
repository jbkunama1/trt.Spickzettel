import os, hmac, hashlib, re
from fastapi import FastAPI, Request, Response, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
from . import store
from .parser import parse
from .pdfgen import make_pdf, list_fonts
from .themes import THEMES

app=FastAPI(title="Spickzettel")
PW=os.getenv("ADMIN_PASSWORD","bitte-aendern"); KEY=os.getenv("SECRET_KEY","dev").encode()
LLM_URL=os.getenv("LLM_URL",""); LLM_MODEL=os.getenv("LLM_MODEL","local")
def token(): return hmac.new(KEY,PW.encode(),hashlib.sha256).hexdigest()
def need_admin(r:Request):
    if not hmac.compare_digest(r.cookies.get("adm",""),token()): raise HTTPException(401,"Admin-Login nötig")

class Inp(BaseModel):
    text:str; title:str|None=None; subtitle:str|None=None; theme:str|None=None; save:bool=False
    overrides:dict={}
def prep(i:Inp):
    s=store.get_settings()
    s.update({k:v for k,v in i.overrides.items() if k in ("theme","orientation","base_size","autofit")})
    if i.theme in THEMES: s["theme"]=i.theme
    d=parse(i.text,s["split_sentences"])
    if i.title: d["title"]=i.title
    return d,s

@app.get("/healthz")
def hz(): return {"ok":True}
@app.get("/api/config")
def config(): return {"settings":store.get_settings(),"themes":THEMES,"fonts":list_fonts(),"llm":bool(LLM_URL)}
@app.post("/api/preview")
def preview(i:Inp):
    d,s=prep(i); return {"data":d,"theme":THEMES[s["theme"]],"settings":s}
@app.post("/api/pdf")
def pdf(i:Inp):
    d,s=prep(i)
    if not d["sections"] and not d["merk"]: raise HTTPException(400,"Kein Inhalt erkannt")
    b,pages,size=make_pdf(d,s)
    if i.save: store.add_history({"title":d["title"],"text":i.text,"theme":s["theme"]})
    fn=re.sub(r"[^A-Za-z0-9ÄÖÜäöüß_-]+","_",d["title"])[:60]+".pdf"
    return Response(b,media_type="application/pdf",headers={"Content-Disposition":f'inline; filename="{fn}"',"X-Pages":str(pages),"X-Fontsize":str(size),"Access-Control-Expose-Headers":"X-Pages,X-Fontsize"})
@app.get("/api/history")
def hist(): return store.history()

@app.post("/api/condense")
async def condense(i:Inp):
    if not LLM_URL: raise HTTPException(501,"LLM_URL nicht gesetzt")
    prompt="Kürze die folgende Unterrichtsverlaufsplanung zu einem Spickzettel in großer Schrift: Behalte die Überschriften (z. B. '1. Einstieg – 5 Min.'), pro Abschnitt max. 3-4 kurze Stichpunkte mit '- ' beginnend, am Ende eine Zeile 'Merksatz: ...'. Nur Deutsch, nur der Spickzettel-Text."
    async with httpx.AsyncClient(timeout=120) as c:
        r=await c.post(LLM_URL,json={"model":LLM_MODEL,"messages":[{"role":"system","content":prompt},{"role":"user","content":i.text}],"temperature":0.2})
    r.raise_for_status(); return {"text":r.json()["choices"][0]["message"]["content"]}

class Login(BaseModel): password:str
@app.post("/api/admin/login")
def login(l:Login,resp:Response):
    if not hmac.compare_digest(l.password,PW): raise HTTPException(401,"Falsches Passwort")
    resp.set_cookie("adm",token(),httponly=True,samesite="strict",max_age=60*60*24*30); return {"ok":True}
@app.post("/api/admin/logout")
def logout(resp:Response): resp.delete_cookie("adm"); return {"ok":True}
@app.get("/api/admin/me")
def me(r:Request): need_admin(r); return {"ok":True}
@app.put("/api/admin/settings")
async def put_settings(r:Request):
    need_admin(r); return store.save_settings(await r.json())
@app.post("/api/admin/font")
async def font(r:Request,file:UploadFile=File(...)):
    need_admin(r)
    if not file.filename.lower().endswith(".ttf"): raise HTTPException(400,"Nur .ttf")
    name=re.sub(r"[^A-Za-z0-9_-]","",file.filename[:-4])
    (store.DATA/"fonts"/f"{name}.ttf").write_bytes(await file.read()); return {"fonts":list_fonts()}
@app.delete("/api/admin/history/{i}")
def dh(i:int,r:Request): need_admin(r); store.del_history(i); return {"ok":True}

@app.get("/")
def index(): return FileResponse("app/static/index.html")
@app.get("/admin")
def admin(): return FileResponse("app/static/admin.html")
app.mount("/static",StaticFiles(directory="app/static"),name="static")
