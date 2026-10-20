---
title: '172\. spotkanie Wroc.NET – Ultra-wydajność i panel: kiedy .NET wystarcza?'
date: 2026-11-17
time: "18:00:00"
categories: spotkania
tags:
  - offline
meetup_attendees: 0
header:
  teaser: /assets/images/spotkania-teaser.jpg
talks:
- title: 'Ultra-wydajność - gdy liczy się każda mikrosekunda'
  speaker_ids:
  - piotr-gankiewicz
- title: 'Kiedy .NET wystarcza, a kiedy warto wyjść poza niego?'
  speaker_ids:
  - piotr-gankiewicz
  - lukasz-olbromski
  - lukasz-pyrzyk
---

172. spotkanie Wrocławskiej Grupy .NET odbędzie się 17.11.2026 r. o **18:00** w **Pubie Wędrówki, ul. Podwale 37/38, 50-040 Wrocław**.

{% include attendance.html %}

{% include talk.html index=0 %}

W wysokowydajnych systemach rozproszonych opóźnienia na poziomie infrastruktury kumulują się pomiędzy kolejnymi serwisami wymieniającymi komunikaty. Nieprzewidywalne skoki latencji, szczególnie te widoczne na wysokich percentylach, potrafią znacząco wpłynąć na wydajność całego systemu i doświadczenia użytkowników.

Współczesny sprzęt oferuje ogromne możliwości, ale samo dorzucanie kolejnych rdzeni i gigabajtów RAM-u nie rozwiązuje wszystkich problemów. Przy odpowiedniej skali nawet pozornie niewielkie narzuty, dodatkowe alokacje pamięci, pauzy GC czy nadmiarowe kopiowanie danych zaczynają mieć znaczenie. Jak więc projektować systemy, które potrafią wycisnąć maksimum z dostępnego sprzętu, zachowując przy tym przewidywalne opóźnienia?

Porozmawiajmy więc o architekturze stworzonej z myślą o takich wymaganiach: thread-per-core, shared-nothing, io_uring, zero-copy czy Viewstamped Replication Revisited. To tylko część mechanizmów, dzięki którym w Apache Iggy udało nam się osiągnąć latencje poniżej jednej milisekundy, nawet na poziomie p99 i wyższych percentyli.

A przede wszystkim będzie to opowieść o tym, jak inżynierska ciekawość i niezadowolenie z istniejących narzędzi popchnęły nas do stworzenia nowoczesnego rozwiązania open source, które niedawno uzyskało status Top-Level Project w Apache Software Foundation i stało się naszym sposobem na życie :)

**{% include speaker.html id="piotr-gankiewicz" %}**

Współzałożyciel i CTO startupu LaserData, oryginalny twórca Apache Iggy, członek jego PMC oraz kontrybutor open source na prawie pełen etat :)

W poprzednim etapie spędziłem ponad dekadę z C# i .NET-em, pracując m.in. nad systemami wymagającymi wysokiej wydajności oraz efektywnego przetwarzania komunikatów w architekturze rozproszonej.

{% include talk.html index=1 %}

Czy problemem jest technologia, architektura, czy sposób, w jaki z nich korzystamy? **Piotr Gankiewicz, Łukasz Olbromski i Łukasz Pyrzyk** porozmawiają o granicach wydajności .NET, powodach sięgania po Rust oraz kosztach takich decyzji. Od optymalizacji istniejącego systemu po stworzenie własnego narzędzia open source: kiedy to uzasadniony krok, a kiedy niepotrzebna komplikacja?

Zapraszamy uczestników spotkania do zadawania pytań i dzielenia się własnymi doświadczeniami.
