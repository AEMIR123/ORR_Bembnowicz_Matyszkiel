# Szablon sprawozdania

## Laboratoria: Obliczenia Równoległe i Rozproszone

> Dokument jest przeznaczony do stopniowego uzupełniania w trakcie całego cyklu zajęć laboratoryjnych. Celem nie jest długi opis, tylko czytelny zapis decyzji, wyników i wniosków.

## 0. Informacje podstawowe

- **Temat zadania:** Analiza wydajności sekwencyjnego, równoległego i rozproszonego przetwarzania dużego zbioru plików tekstowych z agregacją statystyk
- **Skład zespołu:** Bartosz BEMBNOWICZ, Stanisław MATYSZKIEL
- **Grupa laboratoryjna:** WCY22IL1S0
- **Język programowania:** Python
- **Główna technologia / biblioteka:** multiprocessing (wersja równoległa) oraz protokół HTTP np. z użyciem biblioteki requests i prostego serwera FastAPI (wersja rozproszona)

## 1. Problem i zakres

### 1.1. Problem w 2-3 zdaniach

Projekt polega na wyznaczaniu zbiorczych statystyk (np. całkowita liczba słów, unikalne wyrazy, najczęściej występujące słowa) z bardzo dużego zbioru plików tekstowych. Celem jest zbadanie i porównanie wydajności podejścia sekwencyjnego, równoległego oraz rozproszonego pod kątem czasu wykonania i możliwości skalowania. Analiza pozwoli zidentyfikować narzuty związane z podziałem pracy i komunikacją między węzłami w zależności od rosnącej liczby i rozmiaru przetwarzanych plików.

### 1.2. Wejście

- **Format danych wejściowych:** Pliki tekstowe w formacie .txt. Aplikacja będzie wymuszać odczyt w kodowaniu UTF-8 z parametrem ignorowania błędów, co zabezpieczy długotrwałe benchmarki przed nagłym przerwaniem z powodu pojedynczych, uszkodzonych lub nieobsługiwanych znaków.
- **Przykład wejścia:** Folder zawierający dziesiątki lub setki plików .txt, z których każdy waży od kilku kilobajtów do kilkuset megabajtów.
- **Skąd pochodzą dane:** Otwarty zbiór danych pobrany z internetu (np. paczka recenzji lub artykułów z platformy Kaggle), rozpakowany na dysk w postaci tysięcy osobnych plików tekstowych.

### 1.3. Wynik

- **Co dokładnie ma zwrócić program:** Scalony słownik/strukturę danych zawierającą zagregowane metryki dla całego przetworzonego zbioru (całkowita liczba słów, liczba unikalnych słów, top N najczęściej występujących słów). Zwrócony zostanie również zmierzony czas wykonania.
- **W jakim formacie zapisywany jest wynik:** Zapis do pliku wyniki.json (lub .csv dla metryk wydajnościowych) oraz krótkie podsumowanie i czasy wykonania wypisywane bezpośrednio w konsoli (standardowe wyjście).

### 1.4. Kryterium poprawności

- **Sposób sprawdzania poprawności:** Porównanie wyników generowanych przez warianty równoległy i rozproszony z bazowym wynikiem sekwencyjnym (baseline). Pliki wyniki.json ze wszystkich trzech uruchomień muszą zawierać te same statystyki, w tym m.in. zliczony top N.
- **Minimalny przypadek testowy:** Folder test_data/ zawierający zaledwie 2-3 bardzo małe pliki (po kilka krótkich unikalnych zdań każdy). W tym przypadku statystyki łatwo policzyć ręcznie lub innym skryptem, by utworzyć na twardo sprawdzany wzorzec.
- **Oczekiwany wynik dla małego przykładu:** Po uruchomieniu testu każdy wariant aplikacji zawsze wyrzuci na konsole identyczny json reprezentujący wytyczone statystyki.

### 1.5. Minimalny zakres zadania

Zadanie polega na zliczeniu najpopularniejszych słów z plików ("top N") za pomocą 3 odrębnych architektur:

1. **Wersja sekwencyjna (baseline):** Klasyczny skrypt, czytający pliki jeden po drugim w pętli na jednym wątku aplikacji.
2. **Wersja równoległa:** Skrypt (np. w użyciem multiprocessing) rozdzielający pracę na wiele równoległych procesów na jednym komputerze, przyspieszając pracę wielordzeniowo.
3. **Wersja rozproszona (symulowana - distributed-like):** Uruchomienie aplikacji jako osobnych, całkowicie oderwanych z pamięci programów - nadrzędnego "Koordynatora" i "Robotników" (Workerów). Pliki do policzenia nakazywane są Workerom przez symulowaną sieć (np. przez gniazda Socket TCP/HTTP API na localhoście).
   Minimalną poprawną realizacją na koniec jest włączenie tych trzech programów na kilku rosnących paczkach z plikami połączone z zapisaniem czasów wykonania (zmierzonych stoperem systemowym) na potrzeby stworzenia tabel podsumowujących opłacalność (np. w csv).

### 1.6. Czego świadomie nie robimy

- Odsuwamy się od implementowania profesjonalnych technik NLP dla plików tekstowych (usuwanie stop-words/znaków interpunkcyjnych, konwersja encodingów, lematyzacja). **Wykorzystanie prostej metody `split()` i podstawowej translacji (*maketrans*) to nasze celowe, świadome uproszczenie.** Naszym priorytetem jest badanie paradygmatów zrównoleglenia i rozproszenia zadań (analiza narzutów, komunikacji, dysku), a nie rzetelna analiza lingwistyczna. Prosty `split()` stanowi wystarczający "generator obciążenia" dla procesora, który dobrze imituje właściwą pracę CPU w systemie.
- Nie stawiamy realnego środowiska wielochmurowego/rozszerzonej infrastruktury klastra sprzętowego, ponieważ wariant rozproszony symulowany jest przez sub-procesy ze złączami TCP jako model testowy (architekturę połączoną, distributed-like).
- Nie implementujemy odporności procesów komunikacji workerów (fault-tolerance). Skupiamy się na samym map-reduce, przy założeniu, że system pomiarowy symuluje procesy, w których węzły nigdy nie ulegają losowej awarii ani przeciążeniu żądań.

## 2. Ryzyka na starcie

| Ryzyko        | Dlaczego jest istotne | Jak będzie ograniczane |
| ------------- | --------------------- | ----------------------- |
| Przepełnienie pamięci RAM (OOM) | Wczytanie ogromnych plików rzędu gigabajtów jednorazowo w całości do pamięci (np. `file.read()`) doprowadzi do awarii i zakończenia programu. | Zastosowanie leniwego iterowania po dokumencie – ładowanie linia po linii (`for line in f:`), dzięki czemu bieżące użycie RAM jest minimalne. |
| Zbyt duży narzut systemu w stosunku do czasu na obliczenia | Czas alokowania zadań workerom oraz przesyłania tekstów może okazać się dłuższy niż koszt ich natywnego sekwencyjnego przetworzenia (zjawisko negatywnego skalowania). | Testowanie dla zróżnicowanych rozmiarem paczek korpusów. Poszukiwanie poprawnej granularności rozbicia. Zadania będą wysyłane jako większe paczki uśredniając koszty komunikacji w sieci. |

## 3. Plan danych i skali problemu

### 3.1. Dane wejściowe

| Zestaw | Opis          | Rozmiar       | Do czego służy   |
| ------ | ------------- | ------------- | ------------------ |
| Small  | Pliki tekstowe użyte do weryfikacji logiki, ze ściśle zdefiniowaną zawartością (np. z góry ustalona liczba słów `A` i `B`). | Kilkanaście bajtów | Pełen manualny test poprawności systemu względem testów asercji i weryfikacja logiki słownika zliczeń (sprawdzanie na twardo). |
| Medium | Zbiór realnych, nie za dużych dokumentów tekstowych zebranych z domeny publicznej tj. książki / logi czy pliki CSV. | ~ 10-100 MB | Pełnowymiarowy punkt kontrolny oceny zachowania systemowego narzutu komunikacji przy pierwszych próbach zrównoleglenia zadań. |
| Large  | Skompresowane wcześniej korpusy danych NLP/rozpakowane teksty Wikipedii zawierające wręcz tysiące podzielonych fragmentów artykułów w formacie .txt. | Od 1 GB w górę | Analiza ostateczna i końcowa sprawdzająca stopień uzyskiwanego speedupa, usterki graniczne i testująca odporność na załamania serwerów. |

### 3.2. Parametry skalowania

- Co będzie zwiększane: Łączny wolumen (rozmiar) podawanego korpusu tekstów w katalogu; całkowita objętość oddzielnych plików, a przede wszystkim liczba aktywnych workerów (osobnych procesów/serwerów mapujących).
- Jakie poziomy skali będą testowane: Badane obciążenie systemu rozproszonego oraz wielordzeniowego wariantami z 1 (bazowy narzut na starcie), 2, 4, 8 oraz więcej (jeśli to możliwe do symulacji) procesami pracującymi dla korpusów Medium oraz Large.

## 4. Wersja sekwencyjna

### 4.1. Opis rozwiązania

Skrypt pobiera folder `data`, gdzie za pomocą `glob` wyszukuje pliki `.txt`. Następnie, wszystkie pliki są iterowane w pętli. Kod czyta pliki linia po linii, aby zminimalizować użycie pamięci RAM (*leniwe iterowanie*). Każdy plik jest wczytywany i parsowany przy pomocy standardowej funkcji `split()` (rozdzielenie po białych znakach, po uprzednim oczyszczeniu z interpunkcji). **W skrypcie celowo wyodrębniono niezależny rygorystyczny pomiar czasu I/O (samego odczytu dyskowego `readline()`) oraz czasu CPU (parsowanie tekstu i aktualizacja liczników `Counter`) - pozwala to jednoznacznie diagnozować, czy wąskim gardłem systemu jest dysk czy obliczenia.** Zliczenia statystyczne są realizowane poprzez akumulowanie wystąpień. Program działa jednowątkowo.

### 4.2. Sposób uruchomienia

```bash
# Uruchomienie narzędzia baseline
python src/seq_baseline.py --data data --top 10 --out wyniki_sekwencyjne.json
```

### 4.3. Test poprawności

- Jak uruchomić test: `python src/test_poprawnosci.py`
- Wynik testu: Skrypt dynamicznie tworzy `test_data` z 2 plikami (kilka słów i mała całkowita objętość iteracji). Uruchamiany jest parser i asserty na wyniki końcowe. Pojawi się: `Test poprawności sekwencyjnego zliczania zakończony sukcesem!` w przypadku identyczności oczekiwanego zbioru z uzyskanym z parsera.

### 4.4. Ograniczenia baseline'u

- Niskie wykorzystanie sprzętowe: przetwarzanie blokuje cały proces na jednym rdzeniu z powolnym I/O oraz przetwarzaniem krok po kroku.
- Ładowanie plików i parsowanie do jednego słownika ogranicza możliwości przetwarzania większych ilości plików (pamięć współdzielona i czas pętli).

## 5. Plan wersji równoległej

### 5.1. Co dokładnie będzie równoleglone

Zrównolegleniu podlega funkcja czytająca i parsowana dla niezależnego pliku tekstowego z dysku. Moduł dystrybuuje z listy ścieżek dostępowych pojedyncze pliki do odseparowanych w pamięci procesów typu *worker*.

### 5.2. Jednostka pracy

- Jednostka pracy: Pełny, pojedynczy plik tekstowy `.txt`.
- Dlaczego ten podział ma sens: Obliczenia statystyk słów dla jednego pliku w żaden sposób nie zależą od wyników uzyskanych z innych plików (brak zależności w trakcie liczenia). Zapewnia to izolację pamięciową pozwalającą na szybkie mapowanie pracy.

### 5.3. Scalanie wyników

Gdy dany podproces zakończy mapowanie na powierzonych mu dokumentach, zwraca obiekt `collections.Counter` z danymi statystycznymi oraz pomiarami czasu zliczeń I/O oraz CPU. Wątek główny odbiera te skrawki i łączy je aktualizując sumatora o nazwie `total_word_counts.update(counts)`.

### 5.4. Przewidywane narzuty

- synchronizacja: **mała** - zadania są po prostu przydzielane do puli dyspozycyjno-mapującej. Po zmapowaniu danego pliku proces wyrzuca wygenerowany `Counter` zwrotnie do głównego wątku. Brak sygnałów miedzy samymi elementami potomnymi.
- kopiowanie danych: **duża** - Ponieważ instancje potomne interpretera nie rezydują w przestrzeni współdzielonej, słowniki częściowe wygenerowane na workerach muszą przejść długą i mozolną konwersję (tj. seryjne serializowanie *pickle'm* między kanałami IPC) co może skutecznie zjeść czas.
- start workerów / procesów: **średni/duży** - system operacyjny OS pożąda czasu by odblokowac pule procesów systemowych i wybudzić na nowo interpretery.

## 6. Wersja równoległa

### 6.1. Opis implementacji

Zastosowano moduł `concurrent.futures.ProcessPoolExecutor` powołujący do życia pulę niezależnych procesów wyrywających się z ograniczeń GIL. Program za pomocą `.map()` obdziela obiekty do zadań w tle zachowując natywne pomiary obciążenia procesowego z rozdzieleniem od strumieniowania linii tekstu z dysku.

### 6.2. Konfiguracje testowe

| Konfiguracja | Liczba workerów / wątków / procesów | Uwagi         |
| ------------ | --------------------------------------- | ------------- |
| C1           | 2 procesy robocze (Workery)           | Najmniejsza podziałowa jednostka zrównoleglenia zadań z bazowego wariantu. |
| C2           | 4 procesy robocze (Workery)           | Badanie czy obciążenie skaluje się liniowo po dorzuceniu kolejnego duetu wątków i powiększonego ruchu wejścia-wyjścia na szynie dysku. |
| C3           | Max liczba wspierana przez platformę (`os.cpu_count`) | Utrzymanie pełnego, maksymalnego wykorzystania maszyny hostującej na zadanym zbiorze. |

### 6.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: **Tak**
- Jak to sprawdzono: Nadpisano jednostkę `src/test_poprawnosci.py`. Od teraz uruchamia obydwa paradygmaty (Seq vs Par) na wspólnym repozytorium próbek wejściowych (*test_data/*) i weryfikuje ich równe właściwości za pomocą bloku twardych asercji wymuszając zidentyfikowanie identycznej ilości słów obydwiema ścieżkami logicznymi.

### 6.4. Pierwsze obserwacje

- Zgodność logiki ze zbioru referencyjnego udowadnia poprawność transferu obiektów z biblioteki domyślnej (`Counter`) i brak ubywającej alokacji przesianych słów w próżni.
- Testowanie uruchomione z polecenia test_poprawnosci obnaża dominujący ciężar narzutu względem znikomych obliczeń minimalnego pakietu (test trwał blisko jedną całą sekundę wobec braku natywnej szybkości), tym samym potęguje konieczność wypróbowania wielkiej partycji na dedykowanej uprzęży pomiarowej.

## 7. Plan wersji rozproszonej

### 7.1. Architektura

- coordinator / scheduler: [uzupełnić]
- worker: [uzupełnić]
- co jest wysyłane do workera: [dane / parametry / opis zadania]
- co wraca z workera: [uzupełnić]

### 7.2. Dlaczego to jest naprawdę wariant rozproszony lub distributed-like

[opis miejsca występowania jawnej komunikacji, serializacji albo task shipping]

### 7.3. Partie pracy

- Jak duże są partie: [uzupełnić]
- Dlaczego wybrano taki rozmiar: [uzupełnić]

### 7.4. Przewidywane koszty

- serializacja: [uzupełnić]
- komunikacja: [uzupełnić]
- start workerów: [uzupełnić]
- scalanie wyników: [uzupełnić]

## 8. Wersja rozproszona / distributed-like

### 8.1. Opis implementacji

[krótki opis wariantu końcowego]

### 8.2. Sposób uruchomienia

```bash
# [uzupełnić]
```

### 8.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: [tak / nie]
- Jak to sprawdzono: [uzupełnić]

### 8.4. Ograniczenia środowiska

- [uzupełnić]
- [uzupełnić]

## 9. Benchmark i analiza wyników

### 9.1. Środowisko uruchomieniowe

- system / runtime: [uzupełnić]
- CPU / RAM: [uzupełnić]
- lokalnie / Codespaces / Colab / inne: [uzupełnić]
- biblioteki i wersje: [uzupełnić]

### 9.2. Zasady benchmarku

- Czy wszystkie wersje używają tych samych danych: [tak / nie]
- Liczba powtórzeń: [uzupełnić]
- Czy kontrolowana jest losowość: [tak / nie / nie dotyczy]
- Jak mierzony jest czas: [uzupełnić]

### 9.3. Wyniki

| Rozmiar danych / liczba zadań | Seq | Parallel C1 | Parallel C2 | Distributed C1 | Distributed C2 | Uwagi |
| ------------------------------ | --: | ----------: | ----------: | -------------: | -------------: | ----- |
| [uzupełnić]                  | [ ] |         [ ] |         [ ] |            [ ] |            [ ] | [ ]   |
| [uzupełnić]                  | [ ] |         [ ] |         [ ] |            [ ] |            [ ] | [ ]   |
| [uzupełnić]                  | [ ] |         [ ] |         [ ] |            [ ] |            [ ] | [ ]   |

### 9.4. Dodatkowe metryki

Jeśli dotyczy:

- speedup,
- efficiency,
- koszt startu workerów,
- koszt serializacji,
- jakość wyniku / błąd przybliżenia.

| Metryka       | Wartość     | Komentarz     |
| ------------- | ------------- | ------------- |
| [uzupełnić] | [uzupełnić] | [uzupełnić] |
| [uzupełnić] | [uzupełnić] | [uzupełnić] |

### 9.5. Interpretacja wyników

#### Co rzeczywiście przyspiesza

[uzupełnić]

#### Gdzie pojawia się największy narzut

[uzupełnić]

#### Kiedy dodatkowa złożoność ma sens

[uzupełnić]

#### Kiedy dodatkowa złożoność jest przerostem formy nad treścią

[uzupełnić]

## 10. Peer review i poprawki

### 10.1. Otrzymana recenzja od innego zespołu

- Zespół recenzujący: [uzupełnić]
- Najważniejsze uwagi: [uzupełnić]

### 10.2. Wprowadzone poprawki

| Uwaga         | Czy została wdrożona? | Co zmieniono  |
| ------------- | ----------------------- | ------------- |
| [uzupełnić] | [tak / nie]             | [uzupełnić] |
| [uzupełnić] | [tak / nie]             | [uzupełnić] |

## 11. AI use log

| Data / etap   | Do czego użyto AI | Co zostało przyjęte | Co poprawiono ręcznie |
| ------------- | ------------------ | --------------------- | ---------------------- |
| [uzupełnić] | [uzupełnić]      | [uzupełnić]         | [uzupełnić]          |
| [uzupełnić] | [uzupełnić]      | [uzupełnić]         | [uzupełnić]          |

## 12. Uruchomienie i reprodukowalność

### 12.1. Minimalna instrukcja uruchomienia

```bash
# 1. [uzupełnić]
# 2. [uzupełnić]
# 3. [uzupełnić]
```

### 12.2. Struktura repozytorium / plików

- `src/` lub odpowiednik: [uzupełnić]
- `data/` lub odpowiednik: [uzupełnić]
- skrypty benchmarkowe: [uzupełnić]
- test poprawności: [uzupełnić]

## 13. Wnioski końcowe

### 13.1. Najkrótsze podsumowanie w 3 zdaniach

[uzupełnić]

### 13.2. Co działa dobrze

- [uzupełnić]
- [uzupełnić]

### 13.3. Co nie działa lub działa gorzej niż oczekiwano

- [uzupełnić]
- [uzupełnić]

### 13.4. Najważniejsza lekcja techniczna

[uzupełnić]

## 14. Checklista przed oddaniem

- [ ] Temat, wejście, wyjście i kryterium poprawności są jasno opisane.
- [ ] Istnieje działający baseline sekwencyjny.
- [ ] Istnieje test poprawności lub inny wiarygodny sposób weryfikacji wyniku.
- [ ] Wersja równoległa rozwiązuje ten sam problem co wersja sekwencyjna.
- [ ] Wersja rozproszona lub distributed-like rozwiązuje ten sam problem co baseline.
- [ ] Wszystkie porównania wykonano na porównywalnych danych.
- [ ] W benchmarku użyto kilku rozmiarów danych lub liczby zadań.
- [ ] W benchmarku użyto kilku konfiguracji wykonania.
- [ ] Wnioski opisują nie tylko wynik, ale też źródła narzutu.
- [ ] AI use log został uzupełniony.
- [ ] Da się wskazać minimalny sposób uruchomienia rozwiązania.
