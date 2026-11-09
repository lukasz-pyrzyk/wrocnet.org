# 172. spotkanie Wroc.NET

- `2026-11-17-172-spotkanie.rb`: generator OOXML, Ruby 3.2, bez dodatkowych gemów.
- `2026-11-17-172-spotkanie.pptx`: edytowalna prezentacja po normalizacji w Keynote.
- `2026-11-17-172-spotkanie.pdf`: podgląd tych samych 14 slajdów.

Z katalogu głównego repozytorium:

```bash
ruby slides/172/2026-11-17-172-spotkanie.rb /tmp/wrocnet-172-draft.pptx
python3 -m unittest discover -s slides/172 -p 'test_*.py'
```

Testy wymagają Ruby 3.2 w `PATH`; można też wskazać interpreter zmienną `RUBY`.
Budują prezentację w katalogu tymczasowym, bez nadpisywania finalnego PowerPointa.
Sprawdzają strukturę i relacje OOXML, identyfikatory obiektów, numerację, kolejność,
proporcje logotypów i screenshotów, układ panelistów, kadr QR oraz treści.

Generator składa slajdy w kolejności wyświetlania. Numeracja wynika z ich pozycji,
identyfikatory obiektów są unikalne w każdym slajdzie. Obrazy są dopasowane bez
rozciągania; portrety i tła mają kadr wypełniający ramkę. QR jest kadrowany
z istniejącego obrazu, bez zmiany kodu ani adresu społeczności.

Program grudniowego spotkania pochodzi z posta 173 i bazy prelegentów. Statystyki
pozostają ograniczone do daty spotkania 172. Limit 80 napojów i orientacyjne godziny
zachowano z wejściowej prezentacji; nie są potwierdzone przez post wydarzenia.

Po każdej zmianie generatora odśwież oba pliki wynikowe i obejrzyj wszystkie slajdy.
Przed oddaniem otwórz surowy plik w Keynote, wyeksportuj go ponownie jako PowerPoint
i PDF zgodnie z [warsztatem prezentacji](../../office/WORKFLOWS.md#prezentacje-powerpoint).
Finalny PowerPoint po eksporcie nie będzie binarnie identyczny z surowym OOXML.
