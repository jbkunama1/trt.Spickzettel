# 📋 trt.Spickzettel

![Spickzettel](docs/assets/banner.svg)

![FastAPI](https://img.shields.io/badge/FastAPI-ReportLab-047857?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Portainer-2496ED?style=for-the-badge)
![Themes](https://img.shields.io/badge/Farbvorlagen-8-f97316?style=for-the-badge)
![Port](https://img.shields.io/badge/Port-8085-8b5cf6?style=for-the-badge)

Mobile-first Webapp: UVP-Text einfügen, Farbvorlage wählen, Spickzettel als PDF in großer Schrift exportieren. Admin-Menü für Schriftart, Größen und Formatvorlage. Gedacht für Sport und Technik (Sek I).

## ✨ Bedienung

UVP-Text einfügen (oder Button „Einfügen“) → optional Titel und Farbvorlage → Live-Vorschau prüfen → „PDF erstellen“. Auf dem Handy öffnet sich das Teilen-Menü, am Desktop ein neuer Tab. Auto-Fit verkleinert die Schrift bis zum Mindestwert, damit alles auf eine Seite passt. Erstellte Zettel landen im Verlauf und lassen sich neu laden. Der Entwurf bleibt im Browser gespeichert.

### Eingabeformat

| Element | Schreibweise |
|---|---|
| Titel | Erste Zeile `Spickzettel – …` oder Feld „Titel“ |
| Überschrift | `1. Einstieg – 5 Min.`, `# Abschnitt` oder Zeile in GROSSBUCHSTABEN |
| Stichpunkt | Zeile mit `-`, `•` oder `*` |
| Fließtext | wird (Option) satzweise in Stichpunkte zerlegt |
| Merksatz-Box | `Merksatz:`, `Coaching-Sätze:`, `Tipp:`, `Wichtig:`, `Sicherheit:` |

## ⚙️ Admin (`/admin`)

Passwort-Login (`ADMIN_PASSWORD`). Einstellbar: Schriftart (Vera, Helvetica, Times, Courier oder eigene TTF per Upload), Schriftgrößen für Text/Überschrift/Titel, Zeilenabstand, Rand, 8 Farbvorlagen (Sport Blau, Technik Grün, Orange, Rot, Violett, Petrol, KSC, Schwarz-Weiß), Aufzählungszeichen, Hoch-/Querformat, Auto-Fit, Fußzeile, Datum, Verlauf löschen.

## 🚀 Portainer

1. Freien Port 8085 prüfen.
2. Stacks → Add stack → Repository: `https://github.com/jbkunama1/trt.Spickzettel`, Reference `refs/heads/main`, Compose path `docker-compose.yml`. Bei privatem Repo Authentication mit GitHub-Token aktivieren.
3. `ADMIN_PASSWORD` und `SECRET_KEY` als Stack-Variablen setzen (lang, zufällig).
4. Deploy stack, dann `http://SERVER-IP:8085` öffnen, Admin unter `/admin`.

Compose baut das Image lokal aus dem Dockerfile (`build: .`). Es gibt noch keinen GHCR-Workflow.

## 🐳 Docker Compose

```bash
git clone https://github.com/jbkunama1/trt.Spickzettel.git
cd trt.Spickzettel
cp .env.example .env
joe .env
# ADMIN_PASSWORD und SECRET_KEY setzen!
docker compose up -d --build
```

| Einstellung | Bedeutung |
|---|---|
| ADMIN_PASSWORD | Erforderlich, Login für `/admin` |
| SECRET_KEY | Erforderlich, signiert das Admin-Cookie |
| LLM_URL | Optional, OpenAI-kompatibler Endpunkt (z. B. llama.cpp `/v1/chat/completions`) für „Mit KI kürzen“ |
| LLM_MODEL | Optional, Modellname, Standard `local` |
| Port | 8085:8080 |
| Volume | spickzettel_data → /data (settings.json, history.json, fonts/) |

## 💾 Backup

```bash
docker cp spickzettel:/data ./backup-spickzettel
```

Volume nicht löschen; `docker compose down -v` entfernt Einstellungen, Verlauf und Schriften.

## 🔐 Sicherheit / Fehlersuche

Die Erstellung von PDFs ist ohne Login möglich, nur `/admin` ist geschützt. Für Internetbetrieb HTTPS/Reverse Proxy und Firewall verwenden. Keine Schülerdaten in Spickzettel eintragen. Standardpasswort `bitte-aendern` unbedingt ersetzen.

| Problem | Prüfen |
|---|---|
| Port belegt | Port 8085 im Compose ändern |
| Admin-Login schlägt fehl | ADMIN_PASSWORD in den Stack-Variablen |
| Einstellungen weg nach Update | Volume spickzettel_data vorhanden? |
| Umlaute fehlen | Schrift im Admin auf Vera stellen oder eigene TTF hochladen |
| KI-Button fehlt / Fehler | LLM_URL erreichbar? `docker logs spickzettel` |
| PDF hat 2 Seiten | Auto-Fit aktivieren oder Mindestschrift senken |

## 🧪 Entwicklung

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export ADMIN_PASSWORD=dev SECRET_KEY=dev DATA_DIR=./data
uvicorn app.main:app --reload --port 8080
```

API: `GET /healthz`, `GET /api/config`, `POST /api/preview`, `POST /api/pdf`, `GET /api/history`, `POST /api/condense` (optional KI), Admin-Routen unter `/api/admin/*`. Stand: Parser und PDF-Erzeugung wurden lokal getestet; API, Oberfläche und Docker-Build sind noch nicht live bestätigt.

## 🌐 GitHub Pages und Dateien

`index.html` ist eine statische Projektseite, keine lauffertige App. Aktivierung: Settings → Pages → Deploy from a branch → main → / (root). Erwartete Adresse: https://jbkunama1.github.io/trt.Spickzettel/ (Live-Status nicht bestätigt).

`app/` Anwendung (main, parser, pdfgen, store, themes, static) · `Dockerfile`, `docker-compose.yml` Deployment · `docs/assets/banner.svg` Grafik · `.env.example` Konfigurationsvorlage. Keine LICENSE vorhanden, keine Open-Source-Lizenz behauptet.
