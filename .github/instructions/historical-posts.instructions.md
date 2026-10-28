---
description: "Use when tworzenie lub czyszczenie postów historycznych (sprzed 2012) w _posts/ na podstawie niekompletnych źródeł archiwalnych — anonimizacja danych, front matter, formatowanie agendy i prelekcji."
applyTo: "_posts/200[0-9]-*.md,_posts/201[01]-*.md"
---
# Tworzenie postów historycznych (Spotkania Wroc.NET)

Zasady odtwarzania postów sprzed 2012 roku z niepełnych źródeł archiwalnych. Nie stosuj ich do współczesnych zapowiedzi.

Nazewnictwo plików, front matter i tagi są opisane w [README](../../README.md#adding-a-new-meeting-post), a ogólne zasady edycji i walidacji w [AGENTS.md](../../AGENTS.md).

## Czyszczenie źródeł
Podczas przenoszenia tekstu z plików tekstowych/maili:
- **Anonimizacja**: Absolutnie usuwamy wszystkie adresy e-mail (np. `[xyz@gmail.com](mailto:xyz@gmail.com)`). Zostawiamy tylko imiona i nazwiska.
- **Produkty**: Pogrubiamy nazwy kluczowych technologii przy pierwszym wystąpieniu (np. **Visual Studio 2008**, **SQL Server**).
- **Linki**: Usuwamy niedziałające linki do starych grafik (np. `x-apple-ql-id...`). Jeśli link jest zewnętrzny i niepewny, oznaczamy go jako tekst lub usuwamy.
- **Znaki specjalne**: Upewnij się, że symbole takie jak `™`, `®` są poprawnie zakodowane w UTF-8 (lub usuń je, jeśli psują czytelność).

## Formatowanie archiwalnej treści
- **Wydarzenia specjalne**: bez numeru spotkania, z nazwą pliku `YYYY-MM-DD-nazwa-wydarzenia.md`.
- **Miejsce**: Zawsze na początku posta w formacie: `Miejsce: Nazwa Miejsca, Adres, Miasto`.
- **Agenda**: Jeśli w źródle jest lista godzinowa, zamień ją na tabelę Markdown dla lepszej czytelności:
  ```markdown
  | Czas | Wydarzenie |
  | :--- | :--- |
  | 18:00 | Początek |
  ```
- **Prelekcje**: Korzystaj z `talks`, `speaker_ids` i wspólnego [include talk.html](../../_includes/talk.html), zamiast ręcznych nagłówków. Wzór: [spotkanie 35](../../_posts/2011-05-17-35-spotkanie-wroclawskiej-grupy-net.md).

## Kontrola odtworzonego posta
- Sprawdź, czy w tekście nie ma "śmieci" z konwersji (np. `[]()`, podwójne spacje, urwane zdania).
- Upewnij się, że data w nazwie pliku zgadza się z `date` w Front Matter.
- Jeśli post ma numer, sprawdź czy nie dubluje się z istniejącymi w `_posts/`.
