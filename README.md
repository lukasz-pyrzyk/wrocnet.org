# Wroc.NET

Repozytorium strony [wrocnet.org](https://wrocnet.org) — Wrocławskiej Grupy .NET.

Google Analytics 4 jest skonfigurowane w [_config.yml](_config.yml). [CookieConsent 3.1.0](https://cookieconsent.orestbida.com/) jest hostowany lokalnie i ładuje analitykę wyłącznie po akceptacji, tylko w środowisku `production`. Lokalny podgląd pokazuje baner, ale nie wysyła odsłon do Google. Decyzję można zmienić przez „Ustawienia prywatności” w stopce; wycofanie zgody usuwa cookies GA i odświeża stronę. Kod i licencja biblioteki: [assets/vendor/cookieconsent-3.1.0/](assets/vendor/cookieconsent-3.1.0/).

- [Website Admin](https://github.com/lukasz-pyrzyk/wrocnet.org/blob/main/.github/agents/wrocnet-website-admin.agent.md) — uruchamianie lokalne, Docker, Jekyll, edycja strony i walidacja.
- [Content](https://github.com/lukasz-pyrzyk/wrocnet.org/blob/main/.github/agents/wrocnet-content.agent.md) — komunikacja, newslettery i materiały społeczności.
- [Archiwum komunikacji](https://github.com/lukasz-pyrzyk/wrocnet.org/blob/main/office/content/README.md) — zapis treści i przykłady.
- [Zasady pracy w repozytorium](https://github.com/lukasz-pyrzyk/wrocnet.org/blob/main/AGENTS.md).

Sekcja partnerów na stronie głównej ma dwie poziome sekcje: wyróżnionych partnerów strategicznych oraz responsywną siatkę partnerów i patronów. Kolejne wpisy w [_data/partners.yml](_data/partners.yml) automatycznie tworzą nowe rzędy, bez zmian w szablonie. Gdy wszystkie wpisy `supporting` mają rolę „Patron medialny”, druga sekcja nosi nazwę „Patroni medialni”; przy innych rolach używa neutralnego nagłówka „Partnerzy i patroni”.
Nagłówki i logotypy są wyśrodkowane. Logotypy nie mają ramek ani widocznych podpisów; nazwa i rola każdego partnera znajdują się w tekście alternatywnym (`alt`), który nadaje też dostępną nazwę linkowi.
