# Wroc.NET

Repozytorium strony [wrocnet.org](https://wrocnet.org) — Wrocławskiej Grupy .NET.

Google Analytics 4 jest skonfigurowane w [_config.yml](_config.yml). [CookieConsent 3.1.0](https://cookieconsent.orestbida.com/) jest hostowany lokalnie i ładuje analitykę wyłącznie po akceptacji, tylko w środowisku `production`. Lokalny podgląd pokazuje baner, ale nie wysyła odsłon do Google. Decyzję można zmienić przez „Ustawienia prywatności” w stopce; wycofanie zgody usuwa cookies GA i odświeża stronę. Kod i licencja biblioteki: [assets/vendor/cookieconsent-3.1.0/](assets/vendor/cookieconsent-3.1.0/).

- [Website Admin](https://github.com/lukasz-pyrzyk/wrocnet.org/blob/main/.github/agents/wrocnet-website-admin.agent.md) — uruchamianie lokalne, Docker, Jekyll, edycja strony i walidacja.
- [Content](https://github.com/lukasz-pyrzyk/wrocnet.org/blob/main/.github/agents/wrocnet-content.agent.md) — komunikacja, newslettery i materiały społeczności.
- [Archiwum komunikacji](https://github.com/lukasz-pyrzyk/wrocnet.org/blob/main/office/content/README.md) — zapis treści i przykłady.
- [Zasady pracy w repozytorium](https://github.com/lukasz-pyrzyk/wrocnet.org/blob/main/AGENTS.md).

## Lokalny podgląd

Uruchom Docker, a następnie `./run.sh` i otwórz http://127.0.0.1:4001.
Skrypt po udanym zbudowaniu obrazu zatrzymuje poprzednie lokalne kontenery strony
(także z innych checkoutów), a następnie uruchamia jedną instancję `wrocnet-local`.
Rozpoznaje je po etykiecie `org.wrocnet.local=true` lub starszej nazwie obrazu
`wrocnet-local` (z dowolnym tagiem). Nie zatrzymuje innych aplikacji: jeśli obcy
kontener publikuje port TCP hosta 4001 lub 35730 albo zajmuje nazwę `wrocnet-local`, zgłasza błąd.
Kontenery usunięte w trakcie uruchamiania są pomijane z komunikatem; pozostałe błędy Dockera przerywają start.
Nie uruchamiaj dodatkowych podglądów ręcznym `docker run`; używaj tego skryptu.
Zatrzymanie: Ctrl+C lub `docker stop wrocnet-local`.

## Partnerzy i patroni

Sekcja na stronie głównej pokazuje obok siebie grupy „Partner strategiczny” (większe logo) i „Wspierają nas”, a poniżej oddzielne rzędy „Patronat honorowy” i „Patroni medialni”. Na telefonie grupy układają się jedna pod drugą. Wpisy `supporting` w [_data/partners.yml](_data/partners.yml) z rolą „Patron honorowy” trafiają do grupy honorowej, z rolą „Patron medialny” do medialnej, a pozostałe do „Wspierają nas”. Kolejność w pliku wyznacza kolejność w każdej grupie; puste grupy są ukrywane. Logotypy są wyśrodkowane, a nowe wpisy automatycznie zawijają się do kolejnych rzędów. Patronat honorowy ma większe pole na oficjalny znak z pełnym tytułem, bez przycinania ani zmiany proporcji.
Nagłówki i logotypy są wyśrodkowane. Logotypy nie mają ramek ani widocznych podpisów; nazwa i rola każdego partnera znajdują się w tekście alternatywnym (`alt`), który nadaje też dostępną nazwę linkowi.
Sekcja jest współdzielona ([_includes/partners-section.html](_includes/partners-section.html), style w [assets/css/partners.css](assets/css/partners.css)) przez stronę główną i stronę [Współpraca](_pages/wspolpraca.html) (`/wspolpraca/`).

## Oferta sponsorska

Strona `/wspolpraca/` prezentuje ofertę współpracy i linkuje do PDF [assets/offer/Oferta-WrocNET.pdf](assets/offer/Oferta-WrocNET.pdf). Źródłem PDF jest [assets/offer/Oferta-WrocNET.html](assets/offer/Oferta-WrocNET.html) (slajdy 1920×1080, zdjęcia w `assets/offer/photos/web/`). To strona Jekylla (`noindex`, poza sitemapą): organizatorów bierze z [_data/organizers.yml](_data/organizers.yml), a partnerów z [_data/partners.yml](_data/partners.yml), tak jak strona `/wspolpraca/` (wspólny [_includes/offer-people.html](_includes/offer-people.html)). Ring organizatorów zaczyna się od osoby kontaktowej, a dalej idzie w kolejności z pliku. Rozmiar wybranych logotypów w PDF można dostroić klasą `pl--<nazwa pliku logo>`. Zdjęcia w `photos/web/` są zmniejszone i skompresowane (cel: PDF poniżej 3 MB), więc nowe dodawaj w podobnym rozmiarze. Jeśli w `photos/web/` jest plik o tej samej nazwie co zdjęcie organizatora z `_data/organizers.yml`, oferta użyje tej lżejszej wersji; w przeciwnym razie oryginału.

Po zmianie oferty, organizatorów lub partnerów uruchom lokalny podgląd (`./run.sh`) i wyeksportuj PDF ponownie, np. Edge/Chrome headless:
`msedge --headless=new --no-pdf-header-footer --virtual-time-budget=15000 --print-to-pdf=assets/offer/Oferta-WrocNET.pdf http://127.0.0.1:4001/assets/offer/Oferta-WrocNET.html`

Wersję dla sponsorów (z numerem telefonu, wysyłaną mailem) eksportuj poza repozytorium, podając numer w adresie, żeby nie trafił do repo: `--print-to-pdf=<katalog poza repo>\Oferta-WrocNET-sponsorzy.pdf "http://127.0.0.1:4001/assets/offer/Oferta-WrocNET.html?tel=%2B48%20XXX%20XXX%20XXX"`.
Statystyki na stronie liczy [_includes/community-stats-data.html](_includes/community-stats-data.html) (wspólne ze stroną główną i `llms.txt`).
