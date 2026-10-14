import io, datetime
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
from .themes import THEMES
from .store import DATA

RL = Path(reportlab.__file__).parent/"fonts"
BUILTIN = {"Vera":("Vera.ttf","VeraBd.ttf","VeraIt.ttf","VeraBI.ttf"),
           "Helvetica":None,"Times-Roman":None,"Courier":None}
_reg=set()

def list_fonts():
    f=list(BUILTIN)
    f+= sorted(p.stem for p in (DATA/"fonts").glob("*.ttf"))
    return f

def _family(name):
    """returns (regular, bold)"""
    if name=="Helvetica": return "Helvetica","Helvetica-Bold"
    if name=="Times-Roman": return "Times-Roman","Times-Bold"
    if name=="Courier": return "Courier","Courier-Bold"
    if name in _reg: return name,name+"-B"
    if name=="Vera":
        pdfmetrics.registerFont(TTFont("Vera",str(RL/"Vera.ttf")))
        pdfmetrics.registerFont(TTFont("Vera-B",str(RL/"VeraBd.ttf")))
    else:
        p=DATA/"fonts"/f"{name}.ttf"
        if not p.exists(): return _family("Vera")
        pdfmetrics.registerFont(TTFont(name,str(p)))
        b=DATA/"fonts"/f"{name}-Bold.ttf"
        pdfmetrics.registerFont(TTFont(name+"-B",str(b if b.exists() else p)))
    _reg.add(name); return name,name+"-B"

def _build(data, s, scale):
    th=THEMES.get(s["theme"],THEMES["technik_gruen"])
    reg,bold=_family(s["font"])
    P=colors.HexColor(th["primary"]); A=colors.HexColor(th["accent"]); T=colors.HexColor(th["tint"]); X=colors.HexColor(th["text"])
    bs=s["base_size"]*scale; hs=s["heading_size"]*scale; ts=s["title_size"]*scale; ls=s["line_spacing"]
    page=landscape(A4) if s["orientation"]=="landscape" else A4
    m=s["margin_mm"]*mm
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=page,leftMargin=m,rightMargin=m,topMargin=m,bottomMargin=m+(6*mm if s["footer"] or s["show_date"] else 0),title=data["title"])
    W=page[0]-2*m
    st_title=ParagraphStyle("t",fontName=bold,fontSize=ts,leading=ts*1.15,textColor=colors.white)
    st_h=ParagraphStyle("h",fontName=bold,fontSize=hs,leading=hs*1.2,textColor=P,spaceBefore=hs*0.5,spaceAfter=bs*0.2)
    st_b=ParagraphStyle("b",fontName=reg,fontSize=bs,leading=bs*ls,textColor=X,leftIndent=bs*1.1,bulletIndent=0,spaceAfter=bs*0.15)
    st_m=ParagraphStyle("m",fontName=bold,fontSize=bs*1.1,leading=bs*1.1*ls,textColor=X)
    fl=[]
    tb=Table([[Paragraph(escape(data["title"]),st_title)]],colWidths=[W])
    tb.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),P),("LINEBELOW",(0,0),(-1,-1),4,A),
        ("LEFTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    fl+=[tb,Spacer(1,hs*0.3)]
    for sec in data["sections"]:
        blk=[]
        if sec["heading"]:
            h=sec["heading"].upper() if s["heading_caps"] else sec["heading"]
            hp=Paragraph(escape(h),st_h)
            ln=Table([[""]],colWidths=[W],rowHeights=[1.5]); ln.setStyle(TableStyle([("LINEABOVE",(0,0),(-1,0),1.5,A)]))
            blk+=[hp,ln]
        for it in sec["items"]:
            blk.append(Paragraph(escape(it),st_b,bulletText=s["bullet"]))
        fl.append(KeepTogether(blk[:4])); fl+=blk[4:]
    for label,txt in data["merk"]:
        p=Paragraph(f"<font color='{th['primary']}'>{escape(label)}:</font> {escape(txt)}",st_m)
        if s["merk_box"]:
            t=Table([[p]],colWidths=[W]); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),T),("BOX",(0,0),(-1,-1),2,A),
              ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
            fl+=[Spacer(1,bs*0.5),t]
        else: fl+=[Spacer(1,bs*0.5),p]
    foot=" · ".join(x for x in [s["footer"], datetime.date.today().strftime("%d.%m.%Y") if s["show_date"] else ""] if x)
    def onpage(c,d):
        if foot:
            c.setFont(reg,8); c.setFillColor(colors.grey); c.drawString(m,m*0.6,foot)
    doc.build(fl,onFirstPage=onpage,onLaterPages=onpage)
    return buf.getvalue(), doc.page

def make_pdf(data, s):
    scale=1.0
    pdf,pages=_build(data,s,scale)
    if s["autofit"]:
        floor=s["min_size"]/max(s["base_size"],1)
        while pages>1 and scale>floor:
            scale=max(floor,scale-0.04); pdf,pages=_build(data,s,scale)
    return pdf,pages,round(scale*s["base_size"],1)
