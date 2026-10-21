# office/content — Content Archive & Workflow

Scentralizowany katalog dla wszystkich treści Wroc.NET — emaile i ogłoszenia (LinkedIn, Twitter/X, newsletter, grafiki). Jeden płaski folder, typ i data w nazwie pliku (nie w strukturze folderów).

Archiwizujemy tu treści komunikacji i briefy kampanii, także ich wersje robocze. Nie tworzymy osobnych plików `announcement` dla notatek pomocniczych do prezentacji: audytów danych, treści pojedynczych slajdów ani promptów do ich teł. Materiały prezentacji przechowujemy w `slides/<numer-spotkania>/`; dodatkową dokumentację zapisujemy tylko na wyraźną prośbę.

## Struktura

```
office/content/
├── README.md (ten plik)
├── YYYY-MM-DD-TYPE-opis.md   # cała gotowa/robocza treść (email, announcement)
├── images/                  # referencje marki i gotowe grafiki kampanii
└── samples/                 # przykłady maili, ogłoszeń i briefów
```

Wzory do adaptacji: [maile](samples/emails/), [ogłoszenia i newslettery](samples/announcements/), [briefy](samples/briefs/). Zasady tworzenia grafik są w [office/AGENTS.md](../AGENTS.md#zasady-dla-grafik).

## Konwencja nazewnictwa

Wszystkie pliki treści leżą płasko bezpośrednio w `office/content/`:

`YYYY-MM-DD-TYPE-opis.md`

gdzie `TYPE` to jedno z: `email`, `announcement`.

`announcement` to jeden plik na temat/kampanię, zawierający sekcje dla każdego kanału (LinkedIn, Twitter/X, Newsletter) oraz prompty do grafik — nie rozbijaj tego na osobne pliki per kanał.

Przykłady:
- `2026-06-16-announcement-post-meetup-celebration.md`
- `2026-09-05-announcement-call-for-speakers.md`

Grafiki w `images/`:
- `brand-*` — referencje stylu marki (np. `brand-meetup-details-1.jpg`)
- `YYYY-MM-DD-opis.jpg/png/jpeg` — gotowe grafiki konkretnej kampanii (np. `2026-09-05-call-for-speakers-hero.jpeg`)

## Workflow

1. Dostosuj podobny przykład z `samples/`, sprawdzając aktualne dane.
2. Zapisz treść w tym katalogu zgodnie z nazwą i metadanymi poniżej; kolejne wersje aktualizuj w tym samym pliku.
3. Po wysłaniu lub publikacji zmień status i zachowaj datę, kanał oraz znany rezultat. Historię zmian przechowuje Git.
4. W `samples/` utrzymuj wzory do ponownego użycia, nie kopie całych kampanii; do materiałów archiwalnych odsyłaj linkiem.

## Metadane w plikach

Każdy plik powinien zaczynać się od bloku metadata:

```markdown
# [TYPE] [DATE] - [TITLE]
**Context:** [who/when/channel/notes]
**Status:** [template/draft/sent/published]
**Channel:** [LinkedIn/Email/Meetup/Twitter/etc]
---
```

W pliku wielokanałowym używaj nagłówków `##` dla poszczególnych kanałów i grafik.
