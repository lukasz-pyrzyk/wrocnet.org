# office/content — Content Archive & Workflow

Scentralizowany katalog dla wszystkich treści Wroc.NET — emails, posty, newslettery, briefy i szablony.

## Struktura

```
office/content/
├── README.md (ten plik)
├── emails/              # Archiwum wysłanych/gotowych maili
├── posts/               # Archiwum postów (LinkedIn, Twitter, itp.)
├── newsletters/         # Newslettery Meetup.com
├── briefs/              # Krótkie hasła, tagi, opisy do grafik
└── samples/             # Szablony i przykłady do reużycia
    ├── README.md        # Jak używać samples
    ├── emails/          # Email templates
    ├── posts/           # Post templates + examples
    ├── newsletters/     # Newsletter templates
    └── briefs/          # Briefs templates + tags
```

## Workflow

### 1. Piszesz nową treść

- **Sprawdź samples** w `samples/[TYPE]/` — znajdź coś podobnego
- **Adaptuj template** zamiast pisać od zera
- **Personalizuj** dane (daty, nazwiska, kontekst)
- **Aktualizuj metadane** na górze pliku (date, context, status)

### 2. Po wysłaniu/opublikowaniu

- **Przenieś finał** do odpowiedniego folderu (`emails/`, `posts/`, itp.)
- **Zachowaj metadata** (data, kanał, rezultat)
- **Commituj do Git** — historia jest ważna

### 3. Reuzytkalizacja

- Jeśli coś się sprawdziło, **zrób notatkę** w samplach
- **Linkuj do starych wersji** jeśli adaptujesz stary post
- **Dokumentuj wzory** — co działało, co nie

## Konwencje nazewnictwa

### Samples
- `linkedin-examples.md` — przykłady postów LinkedIn
- `pre-meetup-examples.md` — przykłady newsletterów pre-meetup
- `email-templates.md` — szablony maili
- `tags-descriptions-examples.md` — briefs, hashtagi, opisy

### Archiwum (emails/, posts/, newsletters/)
- `YYYY-MM-DD-brief-description.md` — pełny tekst + metadata
- Przykład: `2026-06-16-post-post-meetup-celebration.md`

## Metadane w plikach

Każdy plik powinien zaczynać się od bloku metadata:

```markdown
# [TYPE] [DATE] - [TITLE]
# Context: [who/when/channel/notes]
# Status: [template/draft/sent/published]
# Channel: [LinkedIn/Email/Meetup/Twitter/etc]
---
```

Przykład:
```markdown
# [POST] 2026-06-16 - Post-Meetup Celebration
# Context: After 169. Wroc.NET | LinkedIn | 200+ likes expected
# Status: published
# Channel: LinkedIn
---
```

To ułatwia:
- Wyszukiwanie po dacie, typie, kanale
- Śledzenie co zostało opublikowane
- Szybkie znalezienie starych postów do reuzytkalizacji

## Git Workflow

### Nowy plik w samples (szablonach)
```bash
# Commituj jako template
git add office/content/samples/[TYPE]/filename.md
git commit -m "Add [TYPE] template: [description]"
```

### Finał do archiwum (po wysłaniu)
```bash
# Przenieś z draftu, commituj z datą
git add office/content/[TYPE]/YYYY-MM-DD-description.md
git commit -m "Archive: [TYPE] published on [DATE] - [description]"
```

## Tips

- **Keep samples clean** — nie zaśmiecaj je archiwum; archived files idą do `emails/`, `posts/`, etc.
- **Metadata matters** — zawsze dodaj date, channel, status; szukanie będzie łatwiejsze
- **Reuse aggressively** — jeśli znalazłeś pracujący post, zrób go template
- **Update samples** — co się nauczysz (czemu coś działało/nie), dodaj do README w samples/
- **Short descriptions** — krótki filename, ale descriptive
