# Szablon sprawozdania

## Laboratoria: Obliczenia Równoległe i Rozproszone

> Dokument jest przeznaczony do stopniowego uzupełniania w trakcie całego cyklu zajęć laboratoryjnych. Celem nie jest długi opis, tylko czytelny zapis decyzji, wyników i wniosków.

## 0. Informacje podstawowe

- **Temat zadania:** Analiza wydajności sekwencyjnego, równoległego i rozproszonego przetwarzania dużego zbioru plików tekstowych z agregacją statystyk
- **Skład zespołu:** Bartosz BEMBNOWICZ, Stanisław MATYSZKIEL
- **Grupa laboratoryjna:** WCY22IL1S0
- **Język programowania:** Python
- **Główna technologia / biblioteka:** multiprocessing (wersja równoległa) oraz protokół TCP/IP przy użyciu modułu `multiprocessing.managers.BaseManager` (wersja rozproszona)

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
3. **Wersja rozproszona (symulowana - distributed-like):** Uruchomienie aplikacji jako osobnych, całkowicie oderwanych z pamięci programów - nadrzędnego "Koordynatora" i "Robotników" (Workerów). Pliki do policzenia nakazywane są Workerom przez symulowaną sieć (wykorzystując moduł `BaseManager` wbudowany w bibliotekę standardową `multiprocessing`, nasłuchujący po protokole TCP na porcie `50000`).
   Minimalną poprawną realizacją na koniec jest włączenie tych trzech programów na kilku rosnących paczkach z plikami połączone z zapisaniem czasów wykonania (zmierzonych stoperem systemowym) na potrzeby stworzenia tabel podsumowujących opłacalność (np. w csv).

### 1.6. Czego świadomie nie robimy

- Odsuwamy się od implementowania profesjonalnych technik NLP dla plików tekstowych (usuwanie stop-words/znaków interpunkcyjnych, konwersja encodingów, lematyzacja). **Wykorzystanie prostej metody `split()` i podstawowej translacji (*maketrans*) to nasze celowe, świadome uproszczenie.** Naszym priorytetem jest badanie paradygmatów zrównoleglenia i rozproszenia zadań (analiza narzutów, komunikacji, dysku), a nie rzetelna analiza lingwistyczna. Prosty `split()` stanowi wystarczający "generator obciążenia" dla procesora, który dobrze imituje właściwą pracę CPU w systemie.
- Nie stawiamy realnego środowiska wielochmurowego/rozszerzonej infrastruktury klastra sprzętowego, ponieważ wariant rozproszony symulowany jest przez sub-procesy ze złączami TCP jako model testowy (architekturę połączoną, distributed-like).
- Nie implementujemy odporności procesów komunikacji workerów (fault-tolerance). Skupiamy się na samym map-reduce, przy założeniu, że system pomiarowy symuluje procesy, w których węzły nigdy nie ulegają losowej awarii ani przeciążeniu żądań.

## 2. Ryzyka na starcie

| Ryzyko        | Dlaczego jest istotne | Jak będzie ograniczane |
| ------------- | --------------------- | ----------------------- |
| Przepełnienie pamięci RAM (OOM) | Wczytanie ogromnych plików rzędu gigabajtów jednorazowo w całości do pamięci (np. `file.read()`) doprowadzi do awarii i zakończenia programu. | W wariancie sekwencyjnym i równoległym zastosowano leniwe iterowanie linia po linii (`for line in f:`), minimalizujące użycie RAM. Wariant rozproszony świadomie używa `f.read()` na poziomie Mastera — jest to celowy kompromis: cała treść pliku musi być dostępna jako string przed wysłaniem do workera przez TCP. Ryzyko OOM jest ograniczone przez fakt, że pliki są kolejkowane i przetwarzane jeden po drugim, a nie ładowane równocześnie. |
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

- coordinator / scheduler: Węzeł główny hostujący na wybranym porcie TCP (za pomocą `multiprocessing.managers.BaseManager`) dwie udostępnione w sieci kolejki: `TaskQueue` (zadania) oraz `ResultQueue` (wyniki). Master wczytuje pliki, paczkuje (batchuje) ich zawartość i umieszcza w kolejce, a następnie czeka na wyniki by je zagregować.
- worker: Moduł (proces) kliencki podłączający się przez sieć po adresie IP do Mastera. Wyciąga paczki tekstowe do przerobienia z TaskQueue, dokonuje dekompozycji CPU i wyrzuca zgromadzony wynik do ResultQueue.
- co jest wysyłane do workera: Gotowe, surowe bloki tekstu (połączona zawartość pakietu kilkunastu plików, wielki String) - uniezależnia to Workera od montowania sieciowego dysku wspólnego (NFS).
- co wraca z workera: Zserializowany obiekt `collections.Counter` zawierający wygładzone częstości wyrazów w policzonym bloku, w tym czas CPU workera.

### 7.2. Dlaczego to jest naprawdę wariant rozproszony lub distributed-like

System wykorzystuje jawną komunikację TCP/IP (przez wbudowany w Pythona Socket na `BaseManager`). Architektura zakłada całkowity brak współdzielenia lokalnej pamięci (Shared Memory RAM) pomiędzy menadżerami, a także brak wymogu istnienia współdzielonego dysku sieciowego z logami, ponieważ to infrastruktura "Master" wstrzykuje sam zaserializowany tekst w treść zadania. Umożliwia to zjawisko Task Shipping - realne odpalenie workera na fizycznie innej maszynie, nawet na innej platformie systemowej.

### 7.3. Partie pracy

- Jak duże są partie: Planuje się paczkowanie zawartości odczytanej z kilku mniejszych dokumentów w jednolite bloki tekstu o rozmiarze z rzędu od 1 MB do 5 MB w jedną wiadomość sieciową.
- Dlaczego wybrano taki rozmiar: Celem jest minimalizacja narzutu na komunikację sieciową (Network Overhead). Zlecanie pracy nad każdym pliczkiem z osobna wielkości 1 KB w sieci lokalnej w 95% zużywałoby czas na nawiązywanie połączenia i hand-shake pakietów TCP. Batche amortyzują powolność sieci wobec pracy narzuconej na procesor.

### 7.4. Przewidywane koszty

- serializacja: **Znaczny ciężar**. Treści przesyłane do kolejki muszą przetrwać marshaling/pickling na sieć. Z powrotem wcale nie lżejsze słowniki Counter podróżują na wyjście tej samej ścieżki i powtórnie angażują demarshalling.
- komunikacja: **Umiarkowany w porywach do wysoki** (uzależniony od przepustowości pasma lokalnej łączności Wi-Fi/Ethernet).
- start workerów: **Znikomo obciążające**. Raz zbudowane środowisko pracuje jak nasłuchiwacz, nie jest ciągle zabijane i "wskrzeszane" poza jednorazowym start-upem ręcznym.
- scalanie wyników: **Bardzo mały/Znikomy** koszt. Słowniki po odebraniu ich z serwera, po prostu wpadają do zbiorczej pętli mastera w obiekcie uaktualnienia `total.update()`.

## 8. Wersja rozproszona / distributed-like

### 8.1. Opis implementacji

Aplikacja rozproszona została podzielona na dwa pliki komunikujące się poprzez standard TCP/IP na określonym porcie (klasycznie: `localhost:50000`). Moduł koordynatora (`distributed_master.py`) za pomocą klasy `QueueManager` (dziedziczącej po `BaseManager` z `multiprocessing`) udostępnił kolejki dla "przesyłek". Master zgarnia tekst z plików i pakuje całymi stringami na `TaskQueue`. Drugorzędny moduł workera (`distributed_worker.py`) przypina się jako zdalny klient, pobiera owe paczki tekstowe do przerobienia, zlicza instancją `Counter()` słowa i wrzuca do powrotnej kolejki `ResultQueue` łącznie ze swym czasem CPU. Wstrzykiwanie "pigułek trucizny" (`None` jako end-of-queue) wymusza naturalne wypisywanie się poszczególnych workerów z zadań by nie doprowadzić do wywieszenia sytemu po odeskortowaniu całego korpusu przez plik nadrzędny.

### 8.2. Sposób uruchomienia

```bash
# Uruchomienie głównego serwera (Mastera)
python src/distributed_master.py --data data --top 10 --out wyniki_rozproszone.json

# W innej karcie konsoli / lokalizacji: uruchomienie obróbkowego Workera
python src/distributed_worker.py --ip 127.0.0.1 --port 50000
```

### 8.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: Tak
- Jak to sprawdzono: Zweryfikowano zachowanie programowe po stronie pliku `test_poprawnosci.py`. Nowa funkcja odpala Mastera, a następnie w oddzielnym wątku w tle budzi tymczasowego Workera. Moduł odbiera wynik z węzła komunikacyjnego i w asercji przypasowuje go co do ilości zidentyfikowanych unikalnych elementów oraz częstotliwości względem sekwencyjnego programu bazowego. Test przechodzi spójnie za każdym razem.

### 8.4. Ograniczenia środowiska

- Zjawisko problematycznych asercji Picklers'ów (modułu do serializowania struktur w Pythonie) pod systemem operacyjnym Windows, które wymagają w architekturach Managera podawania do przesyłu jedynie obiektów, struktur i zagnieżdżeń osadzonych "na najwyższym poziomie widoczności w module". Wszelkie labdy czy metody wewnętrzne zwrócą `AttributeError: Can't get local object`. Wymagało to ostrożniejszego wylania w przestrzeń globalną obiektów Queues.
- Zależność od otwartego gniazda TCP i spiętrzenia wymiany portów sprawia, że jednorazowe ubicie serwera w nieodpowiednim momencie uniemożliwi szybkie wznowienie na zajętym od teraz standardowym gnieździe :50000 przez następne kilka sekund. Weryfikacja programowa tego problemu jest bardzo ważna bo test potrafił zgubić kontakt sieciowy gdy nie radził z ponawianiem parowania do nowo budzonego menedżera.
- **Poison Pill — mechanizm łańcuchowego zatrzymania workerów:** Master wrzuca dokładnie jeden `None` do kolejki. Worker, który go odbierze, odkłada `None` z powrotem (mechanizm łańcuchowy), dzięki czemu każdy kolejny worker również dostanie sygnał stopu i wyjdzie. Mechanizm działa poprawnie nawet gdy wiele workerów czeka na `get()` jednocześnie — kolejka FIFO gwarantuje, że tylko jeden worker otrzyma `None` w danej chwili. `timeout=3.0` stanowi dodatkowe zabezpieczenie przed zawieszeniem w przypadku utraty połączenia.

## 9. Benchmark i analiza wyników

### 9.1. Środowisko uruchomieniowe

- system / runtime: MS Windows, Python
- CPU / RAM: Maszyna z co najmniej logcznymi 16 rdzeniami (konfigurowana pod maksymalny test `C3`).
- lokalnie / Codespaces / Colab / inne: Wykonywane testowo "lokalnie" na dyskach obciążanych symetrycznie dla wersji parallel oraz asymetrycznie dla symulacji TCP i gniazd LocalHost (Distributed).
- biblioteki i wersje: Pakiet standardowy (brak zewnętrznych NLP), `multiprocessing.managers`.

### 9.2. Zasady benchmarku

- Czy wszystkie wersje używają tych samych danych: Tak, katalog `data/` w którym wbudowano 9053 pliki z zawartością blisko 201 Mln słów sumarycznie.
- Liczba powtórzeń: Brak iteracji. Po jednym chłodnym na pełnym i jednolitym sprawozdaniu w pętli wielkiej w uprzęży pomiarowej (`benchmark_harness.py`).
- Czy kontrolowana jest losowość: Nie dotyczy, ponieważ w programie licznika użyty jest ten sam, deterministyczny generator mapowania po dysku.
- Jak mierzony jest czas: Użyciem dokładnego sprzętowego timera `time.perf_counter()` oraz ogólnego z uprzęży `time.time()` (aby uwypuklić narzuty rozstawiania socketów w sieci pomiędzy uruchomieniem modułów a rozpoczęciem pracy obrotnicy parsera wyrazów).

### 9.3. Wyniki

> **Uwaga interpretacyjna:** Wyniki dla zestawu mini (2 pliki, 10 słów) są **całkowicie zdominowane przez narzuty startowe** architektur (uruchomienie puli procesów, zestawienie gniazda TCP). Nie należy ich używać do oceny speedupu — służą wyłącznie jako dowód poprawności logiki zliczania. Miarodajne wyniki wydajnościowe to **wyłącznie wiersz z 9053 plikami**. Pliki `.json` zapisane w repozytorium (`wyniki_*.json`) odzwierciedlają uruchomienie na katalogu `test_data` (zestaw mini) i nie są to pliki wynikowe dużego benchmarku — duży benchmark był uruchamiany odrębnie na katalogu `data/`.

| Rozmiar danych / liczba zadań | Seq | Parallel C1 | Parallel C2 | Distributed C1 | Distributed C2 | Uwagi |
| ------------------------------ | --: | ----------: | ----------: | -------------: | -------------: | ----- |
| 2 pliki (wersja mini - 10 słów) | 0.001 s | 0.22 s | 0.20 s | 0.71 s | 0.77 s | **Tylko test poprawności logiki** — wyniki zdominowane przez narzuty architekturowe, nie nadają się do porównań wydajnościowych. |
| 9053 pliki (~201 Mln Słów)          | 252.36 s | 140.86 s | 105.44 s | 78.50 s | 58.95 s | Miarodajne wyniki do analizy speedupu. Raportowany czas „Rzeczywisty” z punktu widzenia timerów we wnętrzu podzespołów aplikacji. |

### 9.4. Dodatkowe metryki

Jeśli dotyczy:

- speedup z punktu architektur,
- jakość narzutu procesowego z powodu osierocenia dysku z limitacji sprzętu.

| Metryka       | Wartość     | Komentarz     |
| ------------- | ------------- | ------------- |
| Symulowany Sppedup rozwiązania Rozproszonego dla C2  | x4.28 | Obliczone jako podział 252.36 s / 58.95 s. Dowodzi, że sieć wieloprocesorowa ugnieciona taktycznie po wierszach omija GIL natywnego Pythona genialnie liniowo z dokładnym skalowaniem. |
| Czas CPU (praca samych modułów) | ~310.2 s (Par Max) | Równoległe procesy C3 pracujące razem wywołały sumaryczny czas rzędu 310 Sekund względem bazowych podliczyliby dla czystego baseline'a sekwencyjnego rzędu 201 s z powodu kosztownego Picklingu i serializacji danych rozproszonych. |

### 9.5. Interpretacja wyników

#### Analiza składowych przyspieszenia (obliczenia, I/O, batchowanie, serializacja)

Przyspieszenie wynika ze współpracy kilku czynników:
- **Obliczenia (CPU):** Rozproszenie żmudnego parsowania (funkcje `split()` i zliczanie częstości) na wiele fizycznych rdzeni maszyny powoduje niemal idealnie liniowy spadek zapotrzebowania na CPU, co wykazuje drastyczny spadek tzw. czasu ściennego.
- **Odciążenie I/O oraz Batchowanie:** Konstrukcja Mastera odczytującego pliki do jednego "Wielkiego Stringa" (duży batch) odciąża same węzły robocze od żądań dyskowych, sprawiając że nie otwierają one plików na własną rękę (brak narzutu na wielokrotne handshaki plikowe na dysku SSD/HDD).
- **Serializacja (narzut vs korzyść):** Choć serializacja pakietów w sieci TCP powoduje zauważalny narzut, korzyści wynikające z podziału gigantycznych paczek znaków deklasują wady tej metody - komunikacja po gnieździe przebiega znacznie płynniej niż oczekiwanie wielu niezależnych podprocesów puli systemowej na deskryptory powolnego wejścia/wyjścia (I/O). W modelu distributed-like wygrywamy zatem na czasie IO dzięki odczytowi i rozesłaniu z poziomu głównego wątku z batchowaniem w pamięci RAM.

#### Gdzie pojawia się największy narzut

Prawdziwym wąskim gardłem systemu nie były narzuty na sieć. Rozbite instancje wielokrotnie sięgające na dysk (Parallel C1 C2 C3) sumowały i odbijały negatywnie wielo-otwarte deskryptory ucinając czas oczekiwania dysku (Wzrost całkowitego narzutu IO systemowego z bazowych 18 sekund na Sekwencji -> do kosmicznych 29 sekund u Parallela dla ułamka jego objętości per worker). System rozproszonego udostępniania TCP pozwolił wymazać narzut IO drastycznie wracając nim do oszczędnych poziomów (9s), ponieważ całe grzebanie plikowe zlecono wyłącznie do odkurzenia po Masterze a Workerom dawano na tacy gorący gotowy kod by połykać serializację. 

#### Kiedy dodatkowa złożoność ma sens

Budowa Mastera rozsyłającego stringi (co jest bez wątpienia dużo cięższe niż użycie biblioteki `concurrent.futures`) okazała się rewelacyjnym lekiem na znany pod Windowsem tryb rozstawiania processów (`spawn system picklers`) - po ominięciu narzutu na każdorazowy transfer plików dyskowych i daniu im zadania rzygniętego przez kolejkę portu, zredukowano koszmar sumarycznego oczekiwania i procesów IO na wolnych dyskach udowadniając wprost, że dodatkowa złożonościowa warstwa portów odnosi genialne skalowanie dla tak wielkich rozrzuconych projektów.

#### Kiedy dodatkowa złożoność jest przerostem formy nad treścią

Nie zalecałoby się wpadania w obłęd symulacji Mastera/Workera, jeżeli nasz zbiór ma kilkadziesiąt/kikaset mega (wielkości próby Medium/Small). Niestabilność połączona z ubijanymi fałszywie Socketami (co doprowadziło by przy złych testach integracyjnych do usterki lub zwieszenia się sprzęciku sieciowego) kosztuje zbyt wiele by uciekać o sekundę lub dwie, a samo ładowanie do bufora menedżera (TaskQueue TCP IP) przyrastałby i dusiło transfer z uwagi na opóźnienia i obłożenie procesora Mastera jeśli plików tekstowych do pocięcia byłoby zaledwie garstka.

## 10. Peer review i poprawki

### 10.1. Otrzymana recenzja (Feedback od prowadzącego na koniec LAB6)

- Prowadzący recenzujący raport zauważył spory potencjał, docenił baseline i logikę wariantu rozproszonego (TCP + BaseManager).
- Najważniejsze uwagi z punktacji (71.5/80): Rozbieżność w raporcie między zapisami użycia FastAPI a realną implementacją pod spodem; brak jasnej instrukcji uruchomienia dla Mastera i Workera; zamazana linia uruchomieniowa między małym testem a dużym benchmarkiem. Zalecono też głębszą i wprost spisaną interpretację wpływu serializacji na przyspieszenie względem I/O w sekcji analizy.

### 10.2. Wprowadzone poprawki (po LAB6)

| Uwaga         | Czy została wdrożona? | Co zmieniono  |
| ------------- | ----------------------- | ------------- |
| Ujednolić opis technologiczny | Tak | Wyrzuciliśmy z raportu wszystkie wzmianki o FastAPI, bo to nie było prawdą — poprawiliśmy na rzeczywisty opis (BaseManager + TCP). |
| Instrukcja uruchomienia Mastera i Workera | Tak | Dopisaliśmy konkretne komendy shellowe jak odpalić mastera i workera ręcznie, żeby nie trzeba było zgadywać. |
| Ułatwienie i oddzielenie testu od benchmarka | Tak | Napisaliśmy jasną instrukcję że `test_poprawnosci` to szybki test logiki, a `benchmark_harness` to ciężki pomiar — żeby nikt ich nie mylił. |
| Analiza składowych speedupu (IO vs serializacja) | Tak | Rozbudowaliśmy sekcję 9.5 — dopisaliśmy o tym czemu batching u mastera pomaga i skąd bierze się narzut IO przy wariancie parallel. |

### 10.3. Otrzymana recenzja peer (Feedback od Grupy 5 na LAB7)

Recenzja dotyczyła wersji projektu po LAB6. Ocena ogólna: projekt kompletny i spójny, wszystkie trzy warianty działają, test poprawności pokrywa wszystkie architektury, wyniki `.json` obecne w repozytorium.

Szczegółowe uwagi:

1. **Niespójność plików `.json` w repo vs opis dużego benchmarku** — Pliki `wyniki_*.json` wskazują na katalog `test_data` (10 słów), a raport opisuje duży benchmark (9053 pliki, 252 s). Wyniki dużego benchmarku nie były udokumentowane osobnymi plikami `.json` w repo.
2. **Sprzeczność w sekcji ryzyk (OOM) vs implementacja mastera** — Tabela ryzyk deklarowała „leniwe iterowanie linia po linii" jako jedyne rozwiązanie OOM, podczas gdy `distributed_master.py` używa `f.read()`. Jest to poprawny kompromis techniczny, jednak niespójny z deklaracją w sekcji ryzyk.
3. **Wyniki mini-danych bez wyraźnego ostrzeżenia** — W tabeli 9.3 zestawione były wyniki mini (0.001 s seq vs 0.77 s dist) obok wyników dużego benchmarku bez zaznaczenia, że pierwsze są bezużyteczne do oceny speedupu i służą wyłącznie weryfikacji poprawności.
4. **Poison Pill — brak dokumentacji mechanizmu łańcuchowego** — Master wysyła jeden `None`; worker przekazuje go dalej łańcuchowo. Działanie jest poprawne, ale nie było opisane w kodzie ani raporcie, co mogło budzić wątpliwości przy wielu równocześnie czekających workerach.

### 10.4. Wprowadzone poprawki (po LAB7 / recenzji peer)

| Uwaga z recenzji | Czy została wdrożona? | Co zmieniono |
| ---------------- | ----------------------- | ------------ |
| Pliki `.json` w repo ≠ wyniki dużego benchmarku | Tak | Dopisaliśmy nad tabelą 9.3 uwagę że pliki `.json` w repo to wyniki z małego `test_data`, a duży benchmark na `data/` był odpalany osobno. |
| OOM risk vs `f.read()` w masterze | Tak | Poprawiliśmy tabelę ryzyk w sekcji 2 — teraz jasno pisze że seq/parallel czyta linia po linii, a master robi `f.read()` bo musi wysłać cały tekst przez TCP. Wyjaśniliśmy czemu to nie jest problem (pliki lecą po kolei, nie wszystkie naraz). |
| Brak ostrzeżenia przy wynikach mini-danych | Tak | Zmieniliśmy opis mini-wiersza w tabeli na „Tylko test poprawności logiki" i dodaliśmy notę nad tabelą żeby było wiadomo który wiersz ma sens do porównań. |
| Poison Pill — brak dokumentacji mechanizmu łańcuchowego | Tak | Opisaliśmy w sekcji 8.4 jak działa łańcuchowe przekazywanie `None` między workerami i po co jest `timeout=3.0`. Dorzuciliśmy też komentarze w kodzie mastera przy `put(None)`. |


## 11. AI use log

| Data / etap   | Do czego użyto AI | Co zostało przyjęte | Co poprawiono ręcznie |
| ------------- | ------------------ | --------------------- | ---------------------- |
| LAB3 | Podrzucenie gotowego kawałka kodu do obsługi argparse w `seq_baseline.py` żeby nie pisać boilerplate'u od zera | Wzięliśmy sam szkielet z flagami `--data`, `--top`, `--out` | Dopisaliśmy sami sprawdzanie czy ścieżka istnieje, obsługę UTF-8 i cały pomiar czasu |
| LAB4 | Zapytaliśmy czemu leci `AttributeError: Can't get local object` przy pickle pod Windowsem w masterze | AI wskazało że `register()` kolejek musi być na poziomie modułu a nie w funkcji | Całą architekturę mastera i mechanizm poison pill pisaliśmy sami, AI tylko pomogło namierzyć ten jeden błąd |
| LAB5 | Podpowiedź jak ładnie sformatować tabelę wyników w Markdown (wyrównanie kolumn) | Skorzystaliśmy z podpowiedzianego formatowania | Dane, opisy i wnioski w tabeli to nasze własne pomiary i przemyślenia |
| LAB6 | Przejrzenie docstringów w `benchmark_harness.py` pod kątem literówek | Poprawiliśmy parę drobnych stylistycznych rzeczy w komentarzach | Sama treść komentarzy i docstringów była nasza od początku |

## 12. Uruchomienie i reprodukowalność

### 12.1. Minimalna instrukcja uruchomienia

W celu weryfikacji funkcjonalnej (mały test poprawności, testujący zliczanie na testowych krótkich plikach):
```bash
python src/test_poprawnosci.py
```

W celu uruchomienia dużego pomiaru statystyk ze wszystkich architektur równoległych i rozproszonych obok siebie (uruchamia Mastera/Workery pod spodem automatycznie na katalogu `data/`):
```bash
python src/benchmark_harness.py
```

Aby "ręcznie" uruchomić architekturę w wariancie rozproszonym (np. na dwóch różnych terminalach po podanej kolejności dla wariantu ręcznego z paczkami korpusów textowych `data`):
```bash
python src/distributed_master.py --data data --top 10 --out wyniki_rozproszone.json
python src/distributed_worker.py --ip 127.0.0.1 --port 50000
```

### 12.2. Struktura repozytorium / plików

- `src/` : Kody źródłowe modułów oraz algorytm główny (wariant rozproszony, wariant zrównoleglony i sekwencyjny).
- `data/` : Katalog przechowujący setki lub tysiące plików tekstowych, stanowiący wejście do skryptów testowych. Zostanie użyty przez benchmark.
- `src/benchmark_harness.py`: Skrypt odpalający duży pomiar łączony oraz ułatwiający odtworzenie całego benchmarku dla obecnych zasobów na danym węźle dla wszystkich implementacji.
- `src/test_poprawnosci.py`: Skrypt jasno oddzielający mały test logiczno-programistyczny z wbudowanymi asercjami od dużego pomiaru wydajności. Warto uruchamiać jako pierwszy do sprawdzania stabilności środowiska.

## 13. Wnioski końcowe

### 13.1. Najkrótsze podsumowanie w 3 zdaniach

Model rozproszony oparty o `BaseManager` (TCP) wykazał się imponującym wzrostem osiągów przy zadaniach operujących na potężnych ilościach plików tekstowych. Głównym czynnikiem determinującym owo zjawisko stało się odizolowanie w czasie procesu odczytywania wejścia IO z dysku przez proces główny Mastera na rzecz wariantu wysyłki zbatchowanych ciągów znaków na workerów w RAMie. Z drugiej strony narzut komunikacyjny na połączenia, serializacja pakietów w sieci TCP na małych plikach zniweczyłyby wszystkie te zalety stąd wymagana jest prawidłowa kategoryzacja i granularność zadania w zależności od powierzonego korpusu wejścia.

### 13.2. Co działa dobrze

- Oddzielenie w pełni logicznego testu poprawnościowego `test_poprawnosci.py` wyposażonego we wbudowane "hardkodowane" na znikomym wygenerowanym folderze testy asertywnościowe bardzo ułatwia weryfikację zmian i logiki przed jakimkolwiek wstrzyknięciem danych na produkcje (benchmark docelowy).
- Zastosowanie modułów wbudowanych standardowej biblioteki (jak BaseManager) perfekcyjnie rozwiązuje sprawę symulowanej rozproszonej komunikacji po gniazdach bez instalowania zewnętrznych potężnych bibliotek.

### 13.3. Co nie działa lub działa gorzej niż oczekiwano

- Narzuty komunikacyjne oraz odtwarzanie (spawning) wątków wieloprocesorowych we wczesnym wariancie Parallel pod Windowsem powodują zjawisko negatywnego skalowania dla malutkich dokumentów, gdzie zadania wykonują się w ułamku sekundy na sekwencyjnym podejściu (tzw. start workerów znacznie zjada procesor na powolnym I/O).
- Stabilność gniazd (sockets): przerwanie skryptu benchmarkowego uśmierca serwer Master bez wcześniejszego eleganckiego rzucenia protokołu trującej pigułki, prowadząc od czasu do czasu do kilkusekundowego zawieszenia i niedostępności portu `50000` na kolejny run.

### 13.4. Najważniejsza lekcja techniczna

Dodatkowa złożoność środowiska i dekompozycji, w tym rozproszenie obciążeń między węzły, okazuje się zbawienna gdy wąskie gardło pojawia się nie tylko w obliczeniach po stronie procesora, ale przede wszystkim w limicie współbieżnych procesów docierających do dysku. Ominięcie narzutu I/O po podziale do RAM i batchowaniu w strumienie TCP uczy, że zrównoleglanie odczytu czasem jest istotniejsze od zrównoleglania samego potoku parsowania tekstu.

## 14. Checklista przed oddaniem

- [x] Temat, wejście, wyjście i kryterium poprawności są jasno opisane.
- [x] Istnieje działający baseline sekwencyjny.
- [x] Istnieje test poprawności lub inny wiarygodny sposób weryfikacji wyniku.
- [x] Wersja równoległa rozwiązuje ten sam problem co wersja sekwencyjna.
- [x] Wersja rozproszona lub distributed-like rozwiązuje ten sam problem co baseline.
- [x] Wszystkie porównania wykonano na porównywalnych danych.
- [x] W benchmarku użyto kilku rozmiarów danych lub liczby zadań.
- [x] W benchmarku użyto kilku konfiguracji wykonania.
- [x] Wnioski opisują nie tylko wynik, ale też źródła narzutu.
- [x] AI use log został uzupełniony (jeśli stosowano we wczesnym etapie).
- [x] Da się wskazać minimalny sposób uruchomienia rozwiązania.
