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
kontener zajmuje port 4001 lub 35730 albo nazwę `wrocnet-local`, zgłasza błąd.
Nie uruchamiaj dodatkowych podglądów ręcznym `docker run`; używaj tego skryptu.
Zatrzymanie: Ctrl+C lub `docker stop wrocnet-local`.

## Partnerzy i patroni

Sekcja na stronie głównej pokazuje obok siebie grupy „Partner strategiczny” (większe logo) i „Wspierają nas”, a poniżej oddzielny rząd „Patroni medialni”. Na telefonie grupy układają się jedna pod drugą. Wpisy `supporting` w [_data/partners.yml](_data/partners.yml) z rolą „Patron medialny” trafiają do grupy medialnej, a pozostałe do „Wspierają nas”. Kolejność w pliku wyznacza kolejność w każdej grupie; puste grupy są ukrywane. Logotypy są wyśrodkowane, a nowe wpisy automatycznie zawijają się do kolejnych rzędów.
Nagłówki i logotypy są wyśrodkowane. Logotypy nie mają ramek ani widocznych podpisów; nazwa i rola każdego partnera znajdują się w tekście alternatywnym (`alt`), który nadaje też dostępną nazwę linkowi.
