# office/content — Content Archive & Workflow

Scentralizowany katalog dla wszystkich treści Wroc.NET — emaile i ogłoszenia (LinkedIn, Twitter/X, newsletter, grafiki). Jeden płaski folder, typ i data w nazwie pliku (nie w strukturze folderów).

## Struktura

```
office/content/
├── README.md (ten plik)
├── YYYY-MM-DD-TYPE-opis.md   # cała gotowa/robocza treść (email, announcement)
├── images/                   # wszystkie grafiki (brand-* referencje + gotowe grafiki kampanii)
│   └── README.md
└── samples/                  # szablony i przykłady do reużycia (osobno, patrz samples/README.md)
```

## Konwencja nazewnictwa

Wszystkie pliki treści leżą płasko bezpośrednio w `office/content/`:

`YYYY-MM-DD-TYPE-opis.md`

gdzie `TYPE` to jedno z: `email`, `announcement`.

`announcement` to jeden plik na temat/kampanię, zawierający sekcje dla każdego kanału (LinkedIn, Twitter/X, Newsletter) oraz sekcję z promptami do grafik (DALL-E/Midjourney) — nie rozbijaj tego na osobne pliki per kanał.

Przykłady:
- `2026-06-16-announcement-post-meetup-celebration.md`
- `2026-09-05-announcement-call-for-speakers.md`

Grafiki w `images/`:
- `brand-*` — referencje stylu marki (np. `brand-meetup-details-1.jpg`)
- `YYYY-MM-DD-opis.jpg/png/jpeg` — gotowe grafiki konkretnej kampanii (np. `2026-09-05-call-for-speakers-hero.jpeg`)

## Workflow

### 1. Piszesz nową treść

- **Sprawdź samples** w `samples/[TYPE]/` — znajdź coś podobnego
- **Adaptuj template** zamiast pisać od zera
- **Personalizuj** dane (daty, nazwiska, kontekst)
- **Aktualizuj metadane** na górze pliku (date, context, status)

### 2. Po wysłaniu/opublikowaniu

- **Zapisz/zaktualizuj plik** bezpośrednio w `office/content/` z nazwą `YYYY-MM-DD-TYPE-opis.md`
- **Zachowaj metadata** (data, kanał, rezultat)
- **Commituj do Git** — historia jest ważna

### 3. Reuzytkalizacja

- Jeśli coś się sprawdziło, **zrób notatkę** w samplach
- **Linkuj do starych wersji** jeśli adaptujesz stary post
- **Dokumentuj wzory** — co działało, co nie

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
# [ANNOUNCEMENT] 2026-06-16 - Post-Meetup Celebration
# Context: After 169. Wroc.NET | LinkedIn | 200+ likes expected
# Status: published
# Channel: LinkedIn
---
```

Dla `announcement` z wieloma kanałami dodaj nagłówek `##` per kanał (LinkedIn, Twitter/X, Newsletter, Grafiki / AI Prompts) zamiast osobnych plików.

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

### Finał treści
```bash
# Commituj z datą w nazwie pliku
git add office/content/YYYY-MM-DD-TYPE-opis.md
git commit -m "Add [TYPE]: [description]"
```

## Tips

- **Keep samples clean** — samples to szablony, gotowa treść żyje płasko w `office/content/`
- **Metadata matters** — zawsze dodaj date, channel, status; szukanie będzie łatwiejsze
- **Reuse aggressively** — jeśli znalazłeś pracujący post, zrób go template
- **Update samples** — co się nauczysz (czemu coś działało/nie), dodaj do README w samples/
- **Short descriptions** — krótki filename, ale descriptive
