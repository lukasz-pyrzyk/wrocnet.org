---
description: "Use when tworzenie lub czyszczenie postów historycznych (sprzed 2012) w _posts/ na podstawie niekompletnych źródeł archiwalnych — anonimizacja danych, front matter, formatowanie agendy i prelekcji."
applyTo: "_posts/**"
---
# Tworzenie postów historycznych (Spotkania Wroc.NET)

Instrukcja dla agentów AI dotycząca procesowania archiwalnych danych spotkań i konferencji.

## Cel
Standaryzacja starych postów (sprzed 2012 roku), które są często odzyskiwane z niekompletnych źródeł, przy zachowaniu spójności z obecnym systemem Jekyll.

## 1. Konwencja nazewnictwa plików
- Jeśli to regularne spotkanie z numerem: `YYYY-MM-DD-NR-spotkanie-wroclawskiej-grupy-net.md`
- Jeśli to wydarzenie specjalne/konferencja: `YYYY-MM-DD-nazwa-wydarzenia.md`
- Data musi być w formacie ISO: `YYYY-MM-DD`.

## 2. Front Matter (YAML)
Zawsze używamy layoutu `single` i kategorii `spotkania`.

```yaml
---
layout: single
title: 'NR. spotkanie Wrocławskiej Grupy .NET' # lub nazwa eventu
categories: spotkania
date: YYYY-MM-DD
---
```

## 3. Czyszczenie treści (Kluczowe)
Podczas przenoszenia tekstu z plików tekstowych/maili:
- **Anonimizacja**: Absolutnie usuwamy wszystkie adresy e-mail (np. `[xyz@gmail.com](mailto:xyz@gmail.com)`). Zostawiamy tylko imiona i nazwiska.
- **Produkty**: Pogrubiamy nazwy kluczowych technologii przy pierwszym wystąpieniu (np. **Visual Studio 2008**, **SQL Server**).
- **Linki**: Usuwamy niedziałające linki do starych grafik (np. `x-apple-ql-id...`). Jeśli link jest zewnętrzny i niepewny, oznaczamy go jako tekst lub usuwamy.
- **Znaki specjalne**: Upewnij się, że symbole takie jak `™`, `®` są poprawnie zakodowane w UTF-8 (lub usuń je, jeśli psują czytelność).

## 4. Formatowanie struktury
- **Miejsce**: Zawsze na początku posta w formacie: `Miejsce: Nazwa Miejsca, Adres, Miasto`.
- **Agenda**: Jeśli w źródle jest lista godzinowa, zamień ją na tabelę Markdown dla lepszej czytelności:
  ```markdown
  | Czas | Wydarzenie |
  | :--- | :--- |
  | 18:00 | Początek |
  ```
- **Prelekcje**: Tytuły prelekcji oznaczamy jako nagłówki `####` z nazwiskiem prelegenta po pauzie `—` (em-dash).

## 5. Walidacja przed zapisem
- Sprawdź, czy w tekście nie ma "śmieci" z konwersji (np. `[]()`, podwójne spacje, urwane zdania).
- Upewnij się, że data w nazwie pliku zgadza się z `date` w Front Matter.
- Jeśli post ma numer, sprawdź czy nie dubluje się z istniejącymi w `_posts/`.
