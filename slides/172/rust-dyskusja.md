# Rust — cytaty i pytania do panelu 172. spotkania Wroc.NET

**Kontekst:** panel „Kiedy .NET wystarcza, a kiedy warto wyjść poza niego?”, 17 listopada 2026.
**Status:** materiał roboczy dla prowadzących, nie do publikacji jako stanowisko Wroc.NET.
**Research:** 17 listopada 2026.

Oryginały cytatów pozostawiono po angielsku. Tłumaczenia i pytania są opracowaniem własnym. Wypowiedzi opisują stanowisko autorów w podanych momentach, niekoniecznie ich aktualne poglądy. Rozróżniono źródła pierwotne i relacje prasowe.

## 1. Mark Russinovich: Rust tam, gdzie potrzebujesz języka bez GC

**Kto i kiedy:** CTO Microsoft Azure, wrzesień 2022.

> “use Rust for those scenarios where a non-GC language is required.”

**Tłumaczenie:** „Używajcie Rusta w tych scenariuszach, w których wymagany jest język bez garbage collectora”.

**Kontekst:** Russinovich postulował zaprzestanie rozpoczynania nowych projektów w C/C++. Kluczowe jest zastrzeżenie „bez GC”: to nie była rekomendacja przepisywania wszystkich aplikacji z C# na Rusta ani ogłoszenie nowej polityki Microsoftu.

**Pytanie na panel:** Co konkretnie musi pokazać pomiar, żeby uznać, że GC rzeczywiście jest problemem, a nie wygodnym podejrzanym?

**Źródło:** [DevClass, 20.09.2022 — relacja przytaczająca wypowiedź](https://devclass.com/2022/09/20/microsoft-azure-cto-on-c-c/). [Oryginalny wpis](https://twitter.com/markrussinovich/status/1571995117233504257) podczas weryfikacji był niedostępny; treść potwierdzono w artykule.

## 2. John Carmack: problemem C++ jest właśnie to, że możesz

**Kto i kiedy:** współtwórca Dooma i Quake'a, 26 stycznia 2019.

> “people don’t look to other languages because you can’t do something in c++, but more often because you can.”

**Tłumaczenie:** „Ludzie nie szukają innych języków dlatego, że czegoś nie da się zrobić w C++, lecz częściej właśnie dlatego, że się da”.

**Kontekst:** odpowiadał na argument, że zalety odkrywane przez twórców gier w Ruście są przecież dostępne również w C++.

**Pytanie na panel:** Czy „możemy ustalić takie zasady w zespole” jest równoważne z „kompilator nie pozwoli ich złamać”? Ile warte są ograniczenia języka?

**Źródło pierwotne:** [wpis Carmacka wraz z kontekstem rozmowy](https://x.com/ID_AA_Carmack/status/1089286703817412608).

## 3. Graydon Hoare: twórca Rusta wybrałby większą prostotę

**Kto i kiedy:** inicjator języka Rust, esej z 2023 roku.

> “I would have traded performance and expressivity away for simplicity”

**Tłumaczenie:** „Poświęciłbym wydajność i siłę wyrazu na rzecz prostoty”.

**Kontekst:** Hoare opisywał różnice między własnymi priorytetami a kierunkiem, w którym poszedł Rust. Prostota oznaczała zarówno mniejsze obciążenie poznawcze użytkownika, jak i prostszy kompilator. Nie jest to stwierdzenie, że Rust poniósł porażkę.

**Pytanie na panel:** Czy ostatnie procenty wydajności są warte większej złożoności kodu i trudniejszego wdrażania ludzi do zespołu? Kto płaci ten koszt?

**Źródło:** [fragmenty eseju przytoczone przez Michaela Tsaia, 8.06.2023](https://mjtsai.com/blog/2023/06/08/the-rust-i-wanted-had-no-future/). [Oryginału](https://graydon2.dreamwidth.org/307291.html) nie udało się bezpośrednio odczytać; cytat zweryfikowano w przytoczeniu.

## 4. Drew DeVault: Rust odziedziczył ambicje C++

**Kto i kiedy:** twórca Sway i SourceHut, 25 marca 2019.

> “Rust is a decent C++ replacement if you have the same goals as C++”

**Tłumaczenie:** „Rust jest przyzwoitym zamiennikiem C++, jeśli macie te same cele co C++”.

**Kontekst:** w eseju „Rust is not a good C replacement” krytykował przede wszystkim rozbudowanie języka. Przeciwstawiał rozwiązywanie problemów przez dodawanie mechanizmów językowych podejściu opartemu na małym, prostym języku.

**Zastrzeżenie:** to historyczna polemika. Autor ostrzega na stronie, że tekst mógł się zestarzeć. Ówczesnych zarzutów dotyczących narzędzi nie należy automatycznie przedstawiać jako opisu obecnego Rusta.

**Pytanie na panel:** Czy przechodząc na Rusta, upraszczamy system, czy zamieniamy złożoność runtime'u na złożoność języka?

**Źródło pierwotne:** [esej DeVaulta](https://drewdevault.com/blog/Rust-is-not-a-good-C-replacement/).

## 5. Linus Torvalds: trudność nie zawsze leży w języku

**Kto i kiedy:** twórca Linuksa, Open Source Summit, czerwiec 2022.

> “People don't understand the VM subsystem, even when it's written in C.”

**Tłumaczenie:** „Ludzie nie rozumieją podsystemu pamięci wirtualnej nawet wtedy, gdy jest napisany w C”.

**Kontekst:** odpowiadał na obawę, że wprowadzenie Rusta utrudni utrzymanie jądra. Zaraz potem zaznaczył, że język zwykle nie jest największą przeszkodą w zrozumieniu kodu.

**Pytanie na panel:** Kiedy mówimy „Rust jest trudny”, ile tej trudności pochodzi z języka, a ile z tego, że zaczynamy jawnie rozwiązywać problemy wcześniej ukryte przez runtime?

**Źródło:** [relacja The Register, 23.06.2022](https://www.theregister.com/2022/06/23/linus_torvalds_rust_linux_kernel/).

## 6. Bryan Cantrill: żałuję, że nie nauczyłem się wcześniej

**Kto i kiedy:** współtwórca DTrace i późniejszy współzałożyciel Oxide, 18 września 2018.

> “if I have one regret about Rust, it’s that I didn’t see beyond the ownership model to learn it earlier.”

**Tłumaczenie:** „Jeśli czegoś żałuję w związku z Rustem, to tego, że nie spojrzałem poza model własności i nie nauczyłem się go wcześniej”.

**Kontekst:** opisywał przepisanie narzędzia do wizualizacji danych. Doceniał nie tylko ownership, lecz także obsługę błędów, makra i ergonomię. Nie ukrywał początkowych potyczek z borrow checkerem.

**Pytanie na panel:** Czy największą korzyścią z Rusta jest szybkość, czy sposób projektowania kodu? Co można przenieść z tych doświadczeń do C#, bez zmieniania platformy?

**Źródło pierwotne:** [„Falling in love with Rust”](https://bcantrill.dtrace.org/2018/09/18/falling-in-love-with-rust/).

## 7. Guido van Rossum: ważne jest utrudnianie obchodzenia zabezpieczeń

**Kto i kiedy:** twórca Pythona, wywiad opisywany w maju 2021.

> “it makes it much harder to bypass the checks in the compiler.”

**Tłumaczenie:** „Znacznie utrudnia obchodzenie kontroli wykonywanych przez kompilator”.

**Kontekst:** tak wyjaśniał jedną z przewag Rusta nad C++. Mówił o bezpieczeństwie zarządzania pamięcią, nie o eliminacji wszystkich kategorii błędów.

**Pytanie na panel:** Skoro C# już zapewnia bezpieczeństwo pamięci w kodzie zarządzanym, jakie dodatkowe argumenty uzasadniają Rust w naszym konkretnym systemie?

**Źródło:** [Slashdot, 23.05.2021 — fragmenty wywiadu](https://developers.slashdot.org/story/21/05/22/0348235/what-python-creator-guido-van-rossum-thinks-of-rust-go-julia-and-typescript).

## 8. John Carmack: miesiąc miodowy z Rustem

**Kto i kiedy:** współtwórca Dooma i Quake'a, 10 lutego 2019.

> “I'm still completely in the excited-newbie honeymoon phase, but writing Rust code feels very wholesome.”

**Tłumaczenie swobodne:** „Wciąż jestem kompletnie w fazie miesiąca miodowego podekscytowanego nowicjusza, ale pisanie w Ruście daje bardzo zdrową satysfakcję”.

**Kontekst:** najlepszy jest tu bezpiecznik dodany przez samego Carmacka: jest zachwycony, ale wie, że dopiero zaczyna.

**Pytanie na panel:** Po czym poznajecie, że nowa technologia rzeczywiście rozwiązuje problem, a nie właśnie przechodzicie z nią miesiąc miodowy?

**Źródło pierwotne:** [wpis Carmacka](https://x.com/ID_AA_Carmack/status/1094419108781789184).

## 9. DHH: Rust jako kwas dla oczu

**Kto i kiedy:** David Heinemeier Hansson, twórca Ruby on Rails (nie języka Ruby); Lex Fridman Podcast #501, transkrypcja opublikowana 26 sierpnia 2026, fragment od 00:49:09.

> “Rust to me is like pouring acid in my eyes when I have to look at the code.”

**Tłumaczenie:** „Patrzenie na kod w Ruście jest dla mnie jak wlewanie sobie kwasu do oczu”.

**Kontekst:** DHH mówi o własnej niechęci do wyglądu i czytania kodu, nie przedstawia tu benchmarku ani argumentu o bezpieczeństwie. Lex dopytuje o przyczynę, a DHH wskazuje estetykę języka. Chwilę później chwali jego właściwości techniczne — dlatego warto pokazać ten cytat razem z następnym.

**Pytanie na panel:** Czy czytelność to wyłącznie kwestia przyzwyczajenia, czy realny koszt biznesowy? Kiedy osobiste preferencje lidera pomagają w wyborze technologii, a kiedy go wypaczają?

**Źródło pierwotne:** [transkrypcja rozmowy, 00:49:09–00:49:53](https://lexfridman.com/dhh-2-transcript/). Wyszukaj w transkrypcji „pouring acid”.

## 10. DHH: odpychający dla ludzi, świetny dla agentów?

**Kto i kiedy:** ta sama rozmowa, wypowiedź od 00:49:53.

> “a wonderful platform for agentic engineering”

**Tłumaczenie:** „Wspaniała platforma do inżynierii z użyciem agentów”.

**Kontekst:** DHH mówi, że mimo niechęci do języka tworzył aplikacje w Ruście. Chwali bezpieczeństwo pamięci, wydajność i przydatność do programowania systemowego. Nie widzi sprzeczności między negatywną oceną ergonomii dla człowieka a pozytywną oceną platformy dla agentów AI.

**Pytania na panel:**

- Jeśli kod generuje AI, czy ergonomia języka przestaje mieć znaczenie, czy wraca ze zdwojoną siłą podczas review i awarii produkcyjnej?
- Czy silniejsze gwarancje kompilatora pozwalają bezpieczniej korzystać z kodu generowanego przez AI? Jakich błędów nadal nie wykryją?
- Czy zespół powinien wdrożyć język, którego sam nie potrafi dobrze debugować, tylko dlatego, że agent sprawnie go generuje?

**Źródło pierwotne:** [transkrypcja rozmowy, 00:49:53–00:50:24](https://lexfridman.com/dhh-2-transcript/). Wyszukaj „wonderful platform”.

### Dodatkowy trop: Rails World 2026 i benchmarki

We wrześniowym keynote DHH wrócił do używania Rusta z AI, zapowiadając zmiany w HEY. To dobry materiał do pytania o zmianę zdania pod wpływem nowych narzędzi, ale nie dowód, że Rails albo ręczne czytanie kodu przestały być potrzebne.

- [Nagranie otwierającego keynote Rails World 2026](https://www.youtube.com/watch?v=vDjW_dRyKXY).
- [Jared Norman, „What About Rails?”, 24.09.2026](https://jardo.dev/what-about-rails) — krytyczna relacja, nie neutralna transkrypcja.
- [The Register, 7.10.2026](https://www.theregister.com/devops/2026/10/07/rails-originator-roasted-over-rust-boosterism/5301494) — opis późniejszego porównania implementacji Campfire w Ruby, Elixirze, Go i Ruście oraz zarzutów dotyczących nierównej optymalizacji.

Nie używać deklarowanych oszczędności HEY ani wyników Campfire jako uniwersalnego mnożnika „Rust kontra Ruby/.NET”. Bez kontroli równoważności funkcjonalnej, architektury i poziomu optymalizacji nie da się przypisać całej różnicy językowi. Wypowiedzi DHH powyżej sprawdzono w transkrypcji podcastu; dodatkowych nagrań nie zweryfikowano przez odsłuch.

## Proponowana kolejność na panel

1. **Rozgrzewka:** Carmack i miesiąc miodowy — kto już zakochał się w nowej technologii?
2. **Konkrety:** Russinovich i brak GC — jaki zmierzony problem uzasadnia zmianę?
3. **Koszty:** Hoare i prostota — ile wydajności potrzeba, a ile kosztuje jej uzyskanie?
4. **Prowokacja:** dwa cytaty DHH razem — czy AI zmienia kryteria wyboru języka?
5. **Domknięcie:** Carmack o ograniczeniach — co chcemy powierzyć kompilatorowi, a co procesowi zespołu?

Na krótszy panel wybrać punkty 1, 2 i 4. Cytaty mają uruchamiać rozmowę o kompromisach, nie zastępować pomiarów autorytetem autora.
