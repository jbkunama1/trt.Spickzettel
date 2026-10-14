import json, os, threading
from pathlib import Path
DATA = Path(os.getenv("DATA_DIR","/data")); DATA.mkdir(parents=True,exist_ok=True)
(DATA/"fonts").mkdir(exist_ok=True)
_lock = threading.Lock()
DEFAULTS = {
 "font":"Vera","base_size":15,"heading_size":18,"title_size":26,"line_spacing":1.25,
 "theme":"technik_gruen","margin_mm":14,"bullet":"•","autofit":True,"min_size":10,
 "split_sentences":True,"footer":"","show_date":False,"orientation":"portrait",
 "heading_caps":True,"merk_box":True,
}
def _rd(name, default):
    p=DATA/name
    try: return json.loads(p.read_text("utf-8"))
    except Exception: return default
def _wr(name,obj):
    with _lock: (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=1),"utf-8")
def get_settings(): return {**DEFAULTS, **_rd("settings.json",{})}
def save_settings(s):
    clean={k:s[k] for k in DEFAULTS if k in s}; _wr("settings.json",{**get_settings(),**clean}); return get_settings()
def history(): return _rd("history.json",[])
def add_history(item):
    h=[i for i in history() if i.get("title")!=item.get("title")]; h.insert(0,item); _wr("history.json",h[:30])
def del_history(i):
    h=history()
    if 0<=i<len(h): h.pop(i); _wr("history.json",h)
