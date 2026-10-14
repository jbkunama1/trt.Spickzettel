import re
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ„\"])")
BUL = re.compile(r"^\s*([-•*–]|\d+\))\s+")
HEAD_NUM = re.compile(r"^\s*\d+[.)]\s+\S")
MERK = re.compile(r"^\s*(Merksatz|Merksätze|Coaching-Sätze|Coaching-Satz|Tipp|Wichtig|Sicherheit)\s*:?\s*(.*)$", re.I)
SKIP = re.compile(r"^(Regeln|Material)\b", re.I)

def _is_head(l):
    s=l.strip()
    if s.startswith("#"): return True
    if HEAD_NUM.match(s) and len(s)<80: return True
    letters=[c for c in s if c.isalpha()]
    return len(s)<50 and len(letters)>=3 and all(c.isupper() for c in letters)

def parse(text, split_sentences=True):
    lines=[l.rstrip() for l in text.replace("\r","").split("\n")]
    title=None; subtitle=None; secs=[]; cur=None; merk=[]
    def new(h): 
        nonlocal cur
        cur={"heading":h,"items":[]}; secs.append(cur)
    i=0
    nonempty=[l for l in lines if l.strip()]
    if nonempty and re.match(r"^\s*(#\s*)?Spickzettel", nonempty[0], re.I):
        title=re.sub(r"^#+\s*","",nonempty[0]).strip()
        lines=lines[lines.index(nonempty[0])+1:]
    para=[]
    def flush():
        nonlocal para
        if not para: return
        t=" ".join(para).strip(); para=[]
        if cur is None: new("")
        parts=SENT.split(t) if split_sentences else [t]
        cur["items"]+= [p.strip() for p in parts if p.strip()]
    for l in lines:
        s=l.strip()
        if not s: flush(); continue
        m=MERK.match(s)
        if m and (m.group(2) or True):
            flush()
            txt=m.group(2).strip()
            if txt: merk.append((m.group(1).capitalize(),txt))
            continue
        if _is_head(s):
            flush(); h=re.sub(r"^#+\s*","",s); h=re.sub(r"^\d+[.)]\s*","",h)
            new(h.strip()); continue
        if BUL.match(s):
            flush()
            if cur is None: new("")
            cur["items"].append(BUL.sub("",s)); continue
        if SKIP.match(s) and len(s)<30: flush(); new(s); continue
        para.append(s)
    flush()
    secs=[s for s in secs if s["heading"] or s["items"]]
    if title is None and secs and not secs[0]["heading"] and secs[0]["items"]:
        title=secs[0]["items"].pop(0)
        if not secs[0]["items"]: secs.pop(0)
    return {"title":title or "Spickzettel","sections":secs,"merk":merk}
