# Spickzettel-Generator

Mobile-first Webapp: UVP-Text einfügen → Spickzettel als PDF (große Schrift, 1 Seite).

## Deployment (Portainer)
1. Repo auf GitHub (dieses Repo).
2. Portainer → Stacks → Add stack → *Repository* → URL, Compose path `docker-compose.yml` (bei privatem Repo: Authentication mit GitHub-Token aktivieren).
3. Environment variables: `ADMIN_PASSWORD`, `SECRET_KEY` (Pflicht ändern!).
4. Deploy → `http://SERVER:8085` (Admin: `/admin`).

## Eingabeformat
- Überschriften: `1. Einstieg – 5 Min.`, `# Titel`, `## Abschnitt` oder GROSSBUCHSTABEN-Zeile
- Stichpunkte: Zeilen mit `-`, `•`, `*`
- Fließtext wird (Option) in Stichpunkte nach Sätzen zerlegt
- `Merksatz: ...` / `Coaching-Sätze: ...` → farbige Box
- Erste Zeile `Spickzettel – ...` wird Titel

## Admin
Schriftart (inkl. eigener TTF-Upload), Größen, Zeilenabstand, Farbvorlage, Ränder, Fußzeile, Auto-Fit (1 Seite), Verlauf.

## Daten
Alles in Volume `/data` (settings.json, history.json, fonts/). Backup = Volume sichern.

## Optional: KI-Kürzen
`LLM_URL` auf z. B. `http://llama:8080/v1/chat/completions` setzen → Button „Mit KI kürzen“.
