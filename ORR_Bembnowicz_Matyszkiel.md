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

- **Co dokładnie ma zwrócić program:** Scaloną strukturę danych (słownik) zawierającą zagregowane metryki dla całego przetworzonego zbioru (całkowita liczba słów, liczba unikalnych słów, top N najczęściej występujących słów). Zwrócony zostanie również zmierzony czas wykonania.
- **W jakim formacie zapisywany jest wynik:** Zapis do pliku wyniki.json (lub .csv dla metryk wydajnościowych) oraz krótkie podsumowanie i czasy wykonania wypisywane bezpośrednio w konsoli (standardowe wyjście).

### 1.4. Kryterium poprawności

- **Sposób sprawdzania poprawności:** Porównanie wyników generowanych przez warianty równoległy i rozproszony z bazowym wynikiem sekwencyjnym (baseline). Pliki wyniki.json ze wszystkich trzech uruchomień muszą zawierać te same statystyki, w tym m.in. zliczony top N.
- **Minimalny przypadek testowy:** Folder test_data/ zawierający zaledwie 2-3 bardzo małe pliki (po kilka krótkich unikalnych zdań każdy). W tym przypadku statystyki łatwo policzyć ręcznie lub innym skryptem, by utworzyć na twardo sprawdzany wzorzec.
- **Oczekiwany wynik dla małego przykładu:** Po uruchomieniu testu każdy wariant aplikacji zawsze wypisze na standardowe wyjście (konsolę) identyczny wynik w formacie JSON, reprezentujący obliczone statystyki.

### 1.5. Minimalny zakres zadania

Zadanie polega na zliczeniu najpopularniejszych słów z plików ("top N") za pomocą 3 odrębnych architektur:

1. **Wersja sekwencyjna (baseline):** Klasyczny skrypt, czytający pliki jeden po drugim w pętli na jednym wątku aplikacji.
2. **Wersja równoległa:** Skrypt (np. z użyciem modułu multiprocessing) rozdzielający pracę na wiele równoległych procesów na jednym komputerze, co pozwala na wielordzeniowe przyspieszenie obliczeń.
3. **Wersja rozproszona (symulowana - distributed-like):** Uruchomienie aplikacji jako osobnych, całkowicie niezależnych w pamięci programów - nadrzędnego "Koordynatora" (Master) i procesów roboczych ("Workerów"). Pliki do przetworzenia przekazywane są Workerom przez symulowaną sieć (wykorzystując moduł `BaseManager` wbudowany w bibliotekę standardową `multiprocessing`, nasłuchujący protokołu TCP na porcie `50000`).
   Minimalną poprawną realizacją na koniec jest uruchomienie tych trzech wariantów na pakietach danych o rosnącym rozmiarze wraz z zapisaniem czasów wykonania (zmierzonych systemowym stoperem) w celu stworzenia tabel podsumowujących skalowalność i opłacalność.

### 1.6. Czego świadomie nie robimy

- Świadomie pomijamy implementację profesjonalnych technik NLP dla plików tekstowych (usuwanie stop-words/znaków interpunkcyjnych, konwersja encodingów, lematyzacja). **Wykorzystanie prostej metody `split()` i podstawowej translacji (*maketrans*) to nasze celowe uproszczenie.** Naszym priorytetem jest badanie paradygmatów zrównoleglenia i rozproszenia zadań (analiza narzutów, komunikacji, dysku), a nie rzetelna analiza lingwistyczna. Prosty `split()` stanowi wystarczający "generator obciążenia" dla procesora, który dobrze symuluje właściwą pracę CPU w systemie.
- Nie stawiamy realnego środowiska wielochmurowego/rozszerzonej infrastruktury klastra sprzętowego, ponieważ wariant rozproszony symulowany jest przez sub-procesy ze złączami TCP jako model testowy (architekturę połączoną, distributed-like).
- Nie implementujemy odporności procesów komunikacji workerów (fault-tolerance). Skupiamy się na samym map-reduce, przy założeniu, że system pomiarowy symuluje procesy, w których węzły nigdy nie ulegają losowej awarii ani przeciążeniu żądań.

## 2. Ryzyka na starcie

| Ryzyko        | Dlaczego jest istotne | Jak będzie ograniczane |
| ------------- | --------------------- | ----------------------- |
| Przepełnienie pamięci RAM (OOM) | Wczytanie ogromnych plików rzędu gigabajtów jednorazowo w całości do pamięci (np. `file.read()`) doprowadzi do awarii i zakończenia programu. | W wariancie sekwencyjnym i równoległym zastosowano leniwe iterowanie linia po linii (`for line in f:`), minimalizujące zużycie pamięci RAM. Wariant rozproszony świadomie używa `f.read()` na poziomie Mastera — jest to celowy kompromis: cała treść pliku musi być dostępna jako string przed wysłaniem do workera przez TCP. Ryzyko OOM jest ograniczone przez fakt, że pliki są kolejkowane i przetwarzane jeden po drugim, a nie ładowane równocześnie. |
| Zbyt duży narzut systemu w stosunku do czasu na obliczenia | Czas alokowania zadań workerom oraz przesyłania tekstów może okazać się dłuższy niż koszt ich natywnego sekwencyjnego przetworzenia (zjawisko negatywnego skalowania). | Testowanie dla zróżnicowanych pod względem rozmiaru pakietów danych. Poszukiwanie optymalnego podziału zadań – wysyłanie większych paczek pozwala zamortyzować koszty komunikacji w sieci. |

## 3. Plan danych i skali problemu

### 3.1. Dane wejściowe

| Zestaw | Opis          | Rozmiar       | Do czego służy   |
| ------ | ------------- | ------------- | ------------------ |
| Small  | Pliki tekstowe użyte do weryfikacji logiki, ze ściśle zdefiniowaną zawartością (np. z góry ustalona liczba słów `A` i `B`). | Kilkanaście bajtów | Pełen test poprawności systemu z użyciem asercji oraz weryfikacja logiki zliczania słów (testy deterministyczne). |
| Medium | Zbiór realnych, nie za dużych dokumentów tekstowych zebranych z domeny publicznej tj. książki / logi czy pliki CSV. | ~ 10-100 MB | Etap pozwalający ocenić narzut na komunikację sieciową przy pierwszych próbach zrównoleglenia zadań. |
| Large  | Skompresowane wcześniej korpusy danych NLP/rozpakowane teksty Wikipedii zawierające tysiące podzielonych fragmentów artykułów w formacie .txt. | Od 1 GB w górę | Analiza końcowa weryfikująca maksymalne przyspieszenie (speedup) oraz testująca odporność i zachowanie aplikacji pod dużym obciążeniem. |

### 3.2. Parametry skalowania

- Co będzie zwiększane: Całkowity rozmiar przetwarzanego zbioru tekstów w katalogu; wielkość poszczególnych plików, a przede wszystkim liczba aktywnych workerów (osobnych procesów/serwerów mapujących).
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
- Wynik testu: Skrypt dynamicznie tworzy `test_data` z 2 plikami (kilka słów i mała objętość danych). Uruchamiany jest parser i asercje weryfikujące wyniki. W przypadku pełnej zgodności wyników na konsoli pojawi się: `Test poprawności sekwencyjnego zliczania zakończony sukcesem!`.

### 4.4. Ograniczenia baseline'u

- Niskie wykorzystanie sprzętowe: przetwarzanie blokuje cały proces na jednym rdzeniu z powolnym I/O oraz przetwarzaniem krok po kroku.
- Ładowanie plików i parsowanie do jednego słownika ogranicza możliwości przetwarzania większych ilości plików (pamięć współdzielona i czas pętli).

## 5. Plan wersji równoległej

### 5.1. Co dokładnie będzie równoleglone

Zrównolegleniu podlega funkcja czytająca i parsująca zawartość niezależnych plików z dysku. Moduł dystrybuuje poszczególne ścieżki plików do odseparowanych w pamięci procesów roboczych (*worker*).

### 5.2. Jednostka pracy

- Jednostka pracy: Pełny, pojedynczy plik tekstowy `.txt`.
- Dlaczego ten podział ma sens: Obliczenia statystyk słów dla jednego pliku w żaden sposób nie zależą od wyników uzyskanych z innych plików (brak zależności w trakcie liczenia). Zapewnia to izolację pamięciową pozwalającą na szybkie mapowanie pracy.

### 5.3. Scalanie wyników

Gdy dany podproces zakończy mapowanie na powierzonych mu dokumentach, zwraca obiekt `collections.Counter` z danymi statystycznymi oraz pomiarami czasu operacji I/O oraz przetwarzania (CPU). Proces główny odbiera te wyniki częściowe i łączy je, aktualizując główny licznik (`total_word_counts.update(counts)`).

### 5.4. Przewidywane narzuty

- synchronizacja: **mała** - zadania są po prostu przydzielane do puli zadań. Po przetworzeniu danego pliku proces przekazuje wygenerowany `Counter` zwrotnie do procesu głównego. Brak komunikacji między poszczególnymi elementami potomnymi.
- kopiowanie danych: **duże** - Ponieważ instancje potomne interpretera nie współdzielą przestrzeni adresowej, słowniki częściowe wygenerowane przez workery muszą zostać poddane konwersji (tj. seryjnej serializacji modułem *pickle* w kanałach IPC), co narzuca istotny koszt czasowy.
- start workerów / procesów: **średni/duży** - system operacyjny wymaga czasu na przydzielenie puli procesów systemowych i uruchomienie nowych instancji interpretera.

## 6. Wersja równoległa

### 6.1. Opis implementacji

Zastosowano moduł `concurrent.futures.ProcessPoolExecutor` powołujący do życia pulę niezależnych procesów, co pozwala pominąć ograniczenia mechanizmu GIL. Program za pomocą metody `.map()` rozdziela zadania, zachowując osobne pomiary czasu procesora (CPU) oraz operacji wejścia/wyjścia (odczyt z dysku).

### 6.2. Konfiguracje testowe

| Konfiguracja | Liczba workerów / wątków / procesów | Uwagi         |
| ------------ | --------------------------------------- | ------------- |
| C1           | 2 procesy robocze (Workery)           | Najmniejsza podziałowa jednostka zrównoleglenia zadań z bazowego wariantu. |
| C2           | 4 procesy robocze (Workery)           | Badanie, czy obciążenie skaluje się liniowo po podwojeniu liczby procesów roboczych i zwiększeniu obciążenia operacjami I/O dysku. |
| C3           | Max liczba wspierana przez platformę (`os.cpu_count`) | Utrzymanie pełnego, maksymalnego wykorzystania maszyny hostującej na zadanym zbiorze. |

### 6.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: **Tak**
- Jak to sprawdzono: Zmodyfikowano skrypt `src/test_poprawnosci.py`. Obecnie uruchamia on obydwa podejścia (sekwencyjne i równoległe) na wspólnym zbiorze próbek testowych (*test_data/*) i weryfikuje ich zgodność za pomocą bloku asercji, sprawdzając, czy obie ścieżki obliczeniowe zwróciły dokładnie te same statystyki.

### 6.4. Pierwsze obserwacje

- Zgodność wyników na zbiorze referencyjnym potwierdza poprawność transferu obiektów `Counter` oraz gwarantuje, że podczas przetwarzania i przesyłania nie dochodzi do utraty zliczonych słów.
- Test poprawności dla minimalnego zestawu danych wyraźnie obnaża dominujący udział narzutów systemowych (start procesów) nad czasem samych obliczeń (test trwał blisko sekundę). Tym samym potwierdza konieczność przeprowadzenia właściwych testów wydajnościowych na dużym zbiorze z użyciem dedykowanego skryptu (benchmarku).

## 7. Plan wersji rozproszonej

### 7.1. Architektura

- coordinator / scheduler: Węzeł główny udostępniający na wybranym porcie TCP (za pomocą `multiprocessing.managers.BaseManager`) dwie kolejki: `TaskQueue` (zadania) oraz `ResultQueue` (wyniki). Master wczytuje pliki, grupuje ich zawartość (tworzy batche) i umieszcza je w kolejce, a następnie czeka na wyniki w celu ich agregacji.
- worker: Moduł (proces) kliencki łączący się przez sieć z Masterem. Pobiera on pakiety tekstowe z `TaskQueue`, analizuje je i przekazuje zagregowany wynik do `ResultQueue`.
- co jest wysyłane do workera: Gotowe bloki tekstu (połączona zawartość kilkunastu plików w formie jednego ciągu znaków) - uniezależnia to Workery od konieczności korzystania ze współdzielonego dysku sieciowego (np. NFS).
- co wraca z workera: Zserializowany obiekt `collections.Counter` zawierający częstości wyrazów dla danego bloku, uzupełniony o zmierzony czas CPU workera.

### 7.2. Dlaczego to jest naprawdę wariant rozproszony lub distributed-like

System wykorzystuje jawną komunikację TCP/IP (przez wbudowany w Pythona Socket na `BaseManager`). Architektura zakłada całkowity brak współdzielenia lokalnej pamięci (Shared Memory RAM) pomiędzy menadżerami, a także brak wymogu istnienia współdzielonego dysku sieciowego z logami, ponieważ to infrastruktura "Master" wstrzykuje sam zaserializowany tekst w treść zadania. Umożliwia to zjawisko Task Shipping - realne odpalenie workera na fizycznie innej maszynie, nawet na innej platformie systemowej.

### 7.3. Partie pracy

- Jak duże są partie: Planuje się agregację zawartości kilkunastu mniejszych dokumentów w jednolite bloki tekstu o rozmiarze rzędu od 1 MB do 5 MB.
- Dlaczego wybrano taki rozmiar: Celem jest minimalizacja narzutu na komunikację sieciową (Network Overhead). Zlecanie pracy nad każdym pojedynczym plikiem o wielkości rzędu 1 KB przez sieć lokalną sprawiłoby, że 95% czasu zajęłoby samo nawiązywanie połączeń i hand-shake TCP. Grupowanie w paczki (batching) amortyzuje opóźnienia sieciowe względem czasu potrzebnego procesorowi na właściwe obliczenia.

### 7.4. Przewidywane koszty

- serializacja: **Znaczny ciężar**. Treści przesyłane do kolejki wymagają czasochłonnej serializacji przed wysłaniem przez sieć. Gotowe wyniki (obiekty Counter) powracające do Mastera są równie duże i wymagają z kolei deserializacji, co pochłania dodatkowy czas procesora.
- komunikacja: **Umiarkowana do wysokiej** (uzależniona od przepustowości pasma lokalnej łączności Wi-Fi/Ethernet).
- start workerów: **Znikomo obciążające**. Raz uruchomione środowisko procesów działa w trybie ciągłego nasłuchiwania i nie musi być ponownie inicjowane (brak narzutu na wielokrotne tworzenie i niszczenie procesów).
- scalanie wyników: **Bardzo mały/Znikomy** koszt. Otrzymane od workerów słowniki są bezpośrednio sumowane w głównej pętli Mastera za pomocą wywołania `total.update()`.

## 8. Wersja rozproszona / distributed-like

### 8.1. Opis implementacji

Aplikacja rozproszona została podzielona na dwa pliki komunikujące się poprzez protokół TCP/IP na określonym porcie (klasycznie: `localhost:50000`). Moduł koordynatora (`distributed_master.py`), za pomocą klasy `QueueManager` (dziedziczącej po `BaseManager` z biblioteki `multiprocessing`), udostępnia kolejki komunikacyjne. Master odczytuje tekst z plików i wysyła zagregowane pakiety tekstowe do `TaskQueue`. Moduł workera (`distributed_worker.py`) łączy się jako zdalny klient, pobiera pakiety danych do przetworzenia, zlicza słowa instancją `Counter()` i przekazuje wynik do kolejki `ResultQueue` wraz z czasem wykonania. Zastosowanie mechanizmu Poison Pill (wartość `None` sygnalizująca koniec zadań) zapewnia bezpieczne zamknięcie workerów i zapobiega zawieszeniu systemu po zakończeniu przetwarzania całego korpusu danych.

### 8.2. Sposób uruchomienia

```bash
# Uruchomienie głównego serwera (Mastera)
python src/distributed_master.py --data data --top 10 --out wyniki_rozproszone.json

# W innej karcie konsoli / lokalizacji: uruchomienie obróbkowego Workera
python src/distributed_worker.py --ip 127.0.0.1 --port 50000
```

### 8.3. Poprawność względem baseline'u

- Czy wynik zgadza się z wersją sekwencyjną: Tak
- Jak to sprawdzono: Wprowadzono test w pliku `test_poprawnosci.py`. Nowa funkcja uruchamia Mastera, a następnie w oddzielnym wątku powołuje do życia tymczasowego Workera. Moduł odbiera wyniki przez sieć i w bloku asercji porównuje je (zarówno liczbę unikalnych słów, jak i ich częstotliwości) z wynikiem referencyjnego programu sekwencyjnego. Test każdorazowo kończy się sukcesem.

### 8.4. Ograniczenia środowiska

- Ograniczenia modułu *pickle* (służącego do serializacji) w systemie Windows, wymagają aby przy użyciu Managera do sieci przesyłać wyłącznie obiekty i funkcje zadeklarowane w głównej przestrzeni nazw modułu (na najwyższym poziomie). Użycie lambd czy funkcji wewnętrznych skutkuje błędem `AttributeError: Can't get local object`. Wymagało to ostrożnego zdefiniowania kolejek i rejestracji w przestrzeni globalnej.
- Zależność od gniazda TCP sprawia, że nagłe przerwanie działania serwera w nieodpowiednim momencie może zablokować port `50000` (stan TIME_WAIT) na kilka sekund. Obsługa wyjątków sieciowych była w tym przypadku kluczowa, gdyż w przeciwnym razie worker mógłby utracić połączenie i nie poradzić sobie z nawiązaniem kontaktu z nowo uruchomionym Masterem.
- **Poison Pill — mechanizm łańcuchowego zatrzymania workerów:** Master wrzuca dokładnie jeden `None` do kolejki. Worker, który go odbierze, odkłada `None` z powrotem (mechanizm łańcuchowy), dzięki czemu każdy kolejny worker również dostanie sygnał stopu i wyjdzie. Mechanizm działa poprawnie nawet gdy wiele workerów czeka na `get()` jednocześnie — kolejka FIFO gwarantuje, że tylko jeden worker otrzyma `None` w danej chwili. `timeout=3.0` stanowi dodatkowe zabezpieczenie przed zawieszeniem w przypadku utraty połączenia.

## 9. Benchmark i analiza wyników

### 9.1. Środowisko uruchomieniowe

- system / runtime: MS Windows, Python
- CPU / RAM: Maszyna z co najmniej 16 rdzeniami logicznymi (skonfigurowana pod maksymalny wariant testowy `C3`).
- lokalnie / Codespaces / Colab / inne: Wykonywane testowo "lokalnie" na dyskach obciążanych symetrycznie dla wersji parallel oraz asymetrycznie dla symulacji TCP i gniazd LocalHost (Distributed).
- biblioteki i wersje: Pakiet standardowy (brak zewnętrznych NLP), `multiprocessing.managers`.

### 9.2. Zasady benchmarku

- Czy wszystkie wersje używają tych samych danych: Tak, katalog `data/` w którym wbudowano 9053 pliki z zawartością blisko 201 Mln słów sumarycznie.
- Liczba powtórzeń: Wykonano pojedyncze uruchomienie na pełnym zbiorze danych, używając skryptu testowego (`benchmark_harness.py`).
- Czy kontrolowana jest losowość: Nie dotyczy, ponieważ w programie licznika użyty jest ten sam, deterministyczny mechanizm iteracji po strukturze katalogów.
- Jak mierzony jest czas: Z użyciem dokładnego licznika `time.perf_counter()` oraz głównego timera w skrypcie pomiarowym `time.time()` (co pozwala uwypuklić narzuty na inicjalizację socketów w sieci względem czasu działania samej pętli przetwarzającej teksty).

### 9.3. Wyniki

> **Uwaga interpretacyjna:** Wyniki dla zestawu mini (2 pliki, 10 słów) są **całkowicie zdominowane przez narzuty startowe** architektur (uruchomienie puli procesów, zestawienie gniazda TCP). Nie należy ich używać do oceny speedupu — służą wyłącznie jako dowód poprawności logiki zliczania. Miarodajnymi wynikami wydajnościowymi są **wyłącznie wartości dla 9053 plików**. Pliki `.json` zapisane w repozytorium (`wyniki_*.json`) odzwierciedlają uruchomienie na katalogu `test_data` (zestaw mini) i nie są to pliki wynikowe dużego benchmarku — duży benchmark był uruchamiany odrębnie na katalogu `data/`.

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
| Speedup rozwiązania rozproszonego dla C2  | x4.28 | Obliczone jako stosunek 252.36 s / 58.95 s. Wynik ten dowodzi, że optymalny podział danych pozwala efektywnie ominąć ograniczenia wynikające z obecności GIL w interpreterze CPython, umożliwiając niemal liniowe skalowanie. |
| Sumaryczny czas CPU workerów | ~310.2 s (Par Max) | Równoległe procesy (C3) osiągnęły sumaryczny czas CPU wynoszący ok. 310 sekund, w porównaniu do 201 sekund dla wersji sekwencyjnej, co wynika z narzutu czasowego związanego z serializacją obiektów (picklingiem). |

### 9.5. Interpretacja wyników

#### Analiza składowych przyspieszenia (obliczenia, I/O, batchowanie, serializacja)

Przyspieszenie wynika ze współpracy kilku czynników:
- **Obliczenia (CPU):** Rozproszenie żmudnego parsowania (funkcja `split()` i zliczanie częstości) na wiele fizycznych rdzeni maszyny pozwala na niemal idealnie liniowe skalowanie, co objawia się drastycznym skróceniem tzw. czasu rzeczywistego (Wall-clock time).
- **Odciążenie I/O oraz Batchowanie:** Konstrukcja Mastera odczytującego pliki do jednego "Wielkiego Stringa" (duży batch) odciąża same węzły robocze od żądań dyskowych, sprawiając że nie otwierają one plików na własną rękę (brak narzutu na wielokrotne handshaki plikowe na dysku SSD/HDD).
- **Serializacja (narzut vs korzyść):** Choć serializacja pakietów w sieci TCP powoduje zauważalny narzut, korzyści wynikające z przesyłania zagregowanych paczek tekstu przewyższają straty z tym związane - transmisja po gnieździe TCP przebiega znacznie płynniej niż konkurowanie wielu niezależnych procesów o dostęp do dysku (I/O). W modelu rozproszonym zyskujemy zatem na czasie odczytu, przenosząc operacje dyskowe wyłącznie do głównego procesu i dystrybuując gotowe paczki danych w pamięci RAM.

#### Gdzie pojawia się największy narzut

Prawdziwym wąskim gardłem systemu nie okazała się sieć, lecz operacje dyskowe. Równoległe procesy robocze (Parallel C1, C2, C3) wielokrotnie sięgające na dysk powodowały nakładanie się na siebie żądań odczytu, co negatywnie wpływało na czasy odpowiedzi dysku (wzrost całkowitego narzutu I/O z 18 sekund w wersji sekwencyjnej do aż 29 sekund w wersji Parallel). System rozproszony oparty na TCP pozwolił na znaczną redukcję narzutu I/O (spadek do ok. 9 sekund), ponieważ odczyt z dysku oddelegowano pojedynczemu wątkowi Mastera, podczas gdy Workery operowały na gotowych partiach danych w pamięci operacyjnej, przy których koszt serializacji okazał się relatywnie niewielki. 

#### Kiedy dodatkowa złożoność ma sens

Zbudowanie środowiska, w którym Master rozsyła dane tekstowe przez sieć, skutecznie zniwelowało problemy związane ze startem procesów w systemie Windows (tzw. metoda `spawn`). Ominięcie narzutu dyskowego oraz bezpośrednie przekazywanie danych do pamięci poszczególnych workerów zredukowało czasy operacji wejścia-wyjścia, udowadniając, że wprowadzenie dodatkowej warstwy komunikacji sieciowej zapewnia doskonałą skalowalność przy przetwarzaniu dużych zestawów danych.

#### Kiedy dodatkowa złożoność jest przerostem formy nad treścią

Architektura Master/Worker nie jest optymalna, jeżeli zbiór danych jest relatywnie mały (np. wielkości próby Medium/Small). Ewentualna niestabilność połączeń i gniazd TCP, a także narzuty czasowe na nawiązywanie połączeń mogą w takich przypadkach przewyższać korzyści z równoległego przetwarzania, dodatkowo nadmiernie obciążając interfejs sieciowy.

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
| Pliki `.json` w repo ≠ wyniki dużego benchmarku | Tak | Dodaliśmy nad tabelą 9.3 informację, że pliki `.json` obecne w repozytorium pochodzą z małego `test_data`, a duży benchmark na katalogu `data/` był uruchamiany niezależnie. |
| OOM risk vs `f.read()` w masterze | Tak | Doprecyzowaliśmy tabelę ryzyk w sekcji 2 — obecnie wyraźnie zaznaczono, że warianty seq/parallel czytają pliki linia po linii, podczas gdy Master wywołuje `f.read()`, aby wysłać kompletny ciąg znaków przez TCP. Wyjaśniono, dlaczego takie podejście jest bezpieczne (pliki buforowane są pojedynczo, a nie ładowane jednocześnie). |
| Brak ostrzeżenia przy wynikach mini-danych | Tak | Zmieniono opis dotyczący małego zestawu danych na „Tylko test poprawności logiki" oraz zamieszczono adnotację nad tabelą, aby jasno wskazać, który wiersz jest miarodajny przy analizie wydajności. |
| Poison Pill — brak dokumentacji mechanizmu łańcuchowego | Tak | Uzupełniono sekcję 8.4 o szczegółowy opis łańcuchowego przekazywania sygnału `None` pomiędzy workerami oraz celowości zastosowania `timeout=3.0`. Dodano również stosowne komentarze w kodzie źródłowym Mastera. |


## 11. AI use log

| Data / etap   | Do czego użyto AI | Co zostało przyjęte | Co poprawiono ręcznie |
| ------------- | ------------------ | --------------------- | ---------------------- |
| LAB3 | Prośba o wygenerowanie struktury `argparse` dla skryptu `seq_baseline.py`, aby uniknąć pisania powtarzalnego kodu (boilerplate) od podstaw. | Wdrożono wygenerowany szkielet logiki parsującej flagi `--data`, `--top` oraz `--out`. | Samodzielnie zaimplementowano sprawdzanie ścieżek, wymuszenie UTF-8 oraz dodano wszystkie pomiary czasowe. |
| LAB4 | Wyszukanie przyczyny występowania błędu `AttributeError: Can't get local object` przy module pickle w środowisku Windows. | Zastosowano sugestię, że wywołanie `register()` dla Managera musi odbywać się w globalnej przestrzeni nazw modułu. | Cała architektura komunikacyjna TCP, jak i mechanizm Poison Pill zostały zaplanowane i napisane ręcznie. |
| LAB5 | Wygenerowanie poprawnego formatowania tabel Markdown dla zestawienia wyników czasowych. | Zaaplikowano schemat i wyrównania zaproponowane przez LLM. | Same pomiary, czasy oraz wnioski do tabel wprowadzono w oparciu o własne wyniki wykonania. |
| LAB6 | Sprawdzenie literówek w komentarzach i dokumentacji w skrypcie `benchmark_harness.py`. | Wprowadzono kilka drobnych poprawek językowych. | Merytoryczna treść komentarzy była autorska od samego początku. |

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

- `src/` : Kody źródłowe modułów oraz algorytm główny (wariant rozproszony, wariant równoległy i sekwencyjny).
- `data/` : Katalog przechowujący setki lub tysiące plików tekstowych, stanowiący wejście do skryptów testowych. Zostanie użyty przez benchmark.
- `src/benchmark_harness.py`: Skrypt odpalający duży pomiar łączony oraz ułatwiający odtworzenie całego benchmarku dla obecnych zasobów na danym węźle dla wszystkich implementacji.
- `src/test_poprawnosci.py`: Skrypt jasno oddzielający mały test logiczno-programistyczny z wbudowanymi asercjami od dużego pomiaru wydajności. Warto uruchamiać jako pierwszy do sprawdzania stabilności środowiska.

## 13. Wnioski końcowe

### 13.1. Najkrótsze podsumowanie w 3 zdaniach

Model rozproszony oparty na `BaseManager` (TCP) wykazał się imponującym wzrostem osiągów przy zadaniach operujących na potężnych ilościach plików tekstowych. Głównym powodem tego wzrostu wydajności jest oddelegowanie operacji wejścia/wyjścia (odczyt z dysku) wyłącznie do procesu Mastera i wysyłanie gotowych, zagregowanych paczek tekstu do workerów pracujących w pamięci RAM. Ponieważ jednak przy małych plikach narzut komunikacyjny (połączenia, serializacja) byłby większy niż zysk z obliczeń, wymagany jest odpowiedni podział zadań w zależności od wielkości przetwarzanego zbioru danych.

### 13.2. Co działa dobrze

- Wykorzystanie skryptu `test_poprawnosci.py` z predefiniowanymi testami i asercjami na minimalnym zbiorze danych znacznie ułatwia weryfikację logiki przed właściwym przetworzeniem pełnego zestawu badawczego.
- Zastosowanie modułów z biblioteki standardowej (takich jak BaseManager) bardzo dobrze rozwiązuje problem rozproszonej komunikacji TCP bez konieczności wprowadzania skomplikowanych zewnętrznych zależności.

### 13.3. Co nie działa lub działa gorzej niż oczekiwano

- Narzuty komunikacyjne oraz odtwarzanie (spawning) procesów w wariancie Parallel pod systemem Windows powodują zjawisko negatywnego skalowania w przypadku bardzo małych dokumentów, gdzie narzut na uruchomienie workerów przewyższa czas potrzebny na faktyczne zliczenie danych, a same operacje wejścia-wyjścia znacząco obciążają dysk.
- Stabilność gniazd (sockets): nagłe przerwanie skryptu zamyka proces Mastera bez uprzedniego przekazania sygnału Poison Pill, co może skutkować kilkusekundową blokadą i niedostępnością portu `50000` przy próbie kolejnego uruchomienia.

### 13.4. Najważniejsza lekcja techniczna

Dodatkowa złożoność środowiska i dekompozycji, w tym rozproszenie obciążeń między węzły, przynosi wymierne korzyści, gdy wąskie gardło pojawia się nie tylko w obliczeniach po stronie procesora, ale przede wszystkim w limitach operacji dyskowych. Zminimalizowanie narzutu I/O dzięki podziałowi paczek w RAM i strumieniowaniu TCP uświadamia, że optymalizacja odczytu plików nierzadko jest ważniejsza niż samo zrównoleglenie parsowania tekstu.

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
