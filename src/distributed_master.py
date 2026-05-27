import os
import glob
import time
import json
from collections import Counter
from multiprocessing.managers import BaseManager
import queue

class QueueManager(BaseManager):
    pass

_task_queue = queue.Queue()
_result_queue = queue.Queue()

def return_task_queue():
    return _task_queue

def return_result_queue():
    return _result_queue

def process_directory_distributed(directory_path, file_pattern="*.txt", address=('127.0.0.1', 50000), authkey=b'orr_secret'):
    """Wczytuje pliki i udostępnia zadania dla aplikacji rozproszonych za pomocą Managera na wskazanym porcie."""
    files = glob.glob(os.path.join(directory_path, file_pattern))
    if not files:
        print(f"Brak plików {file_pattern} w ścieżce {directory_path}")
        return Counter(), 0, 0.0, 0.0

    QueueManager.register('get_task_queue', callable=return_task_queue)
    QueueManager.register('get_result_queue', callable=return_result_queue)

    manager = QueueManager(address=address, authkey=authkey)
    print(f"Uruchamianie serwera koordynatora na porcie {address[1]}...")
    manager.start()
    
    server_task_queue = manager.get_task_queue()
    server_result_queue = manager.get_result_queue()

    total_io_time = 0.0
    num_batches = 0
    
    # Wrzucamy zawartość każdego pliku jako osobne zadanie do kolejki
    print(f"Odczytywanie zawartości z {len(files)} plików...")
    for filepath in files:
        t_io_start = time.perf_counter()
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Błąd czytania {filepath}: {e}")
            continue
        total_io_time += (time.perf_counter() - t_io_start)
        
        if content.strip():
            server_task_queue.put(content)
            num_batches += 1

    print(f"Wysłano {num_batches} porcji tekstu (zadań) do kolejki. Oczekiwanie na przeliczenie...")

    # Czekanie na wyniki
    total_word_counts = Counter()
    total_words = 0
    total_cpu_time = 0.0
    
    for _ in range(num_batches):
        counts, words, cpu_time = server_result_queue.get()
        total_word_counts.update(counts)
        total_words += words
        total_cpu_time += cpu_time
        
    print("Wszystkie wyniki zebrane. Wysyłanie sygnału stopu do workerów...")
    # None jako sygnal stopu (poison pill) - worker ktory go odbierze sam przekaze dalej
    # Sygnal stopu: wrzucamy jeden None. Worker ktory go odbierze, odda go z powrotem do kolejki
    # (mechanizm lancuchowy) - kazdy nastepny worker rowniez odbierze sygnale i takze wyjdzie.
    # Dziala poprawnie nawet jesli wiele workerow czeka na get() jednoczesnie - kolejka FIFO zapewnia,
    # ze tylko jeden worker otrzyma None w danej chwili, po czym odlozy go dla nastepnego.
    server_task_queue.put(None)
    
    # Zamknięcie serwera
    manager.shutdown()
    
    return total_word_counts, total_words, total_io_time, total_cpu_time

def run_distributed(directory_path, top_n=10, output_file="wyniki_rozproszone.json"):
    print(f"Rozpoczęcie rozproszonego przetwarzania na plikach: {directory_path} ...")
    start_time = time.perf_counter()
    
    word_counts, total_words, total_io_time, total_cpu_time = process_directory_distributed(
        directory_path
    )
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    top_words = word_counts.most_common(top_n)
    unique_words = len(word_counts)
    
    results = {
        "metoda": "rozproszona",
        "katalog": directory_path,
        "calkowita_liczba_slow": total_words,
        "liczba_unikalnych_slow": unique_words,
        "top_slowa": top_words,
        "czas_io_sekundy_zsumowany": total_io_time, 
        "czas_cpu_sekundy_zsumowany": total_cpu_time, 
        "czas_wykonania_sekundy": execution_time
    }
    
    print("\n--- Podsumowanie (Rozproszone - MVP) ---")
    print(f"Całkowita liczba słów: {total_words}")
    print(f"Liczba unikalnych słów: {unique_words}")
    print(f"Top {top_n} najczęstszych słów:")
    for word, count in top_words:
        print(f"  {word}: {count}")
    print(f"\nCzas I/O mastera (odczyt plików): {total_io_time:.4f} s")
    print(f"Zsumowany czas CPU workerów: {total_cpu_time:.4f} s")
    print(f"Całkowity czas wykonania: {execution_time:.4f} s\n")

    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Rozproszone zarządzanie koordynatorem (Master).')
    parser.add_argument('--data', type=str, default='data', help='Ścieżka do folderu z danymi')
    parser.add_argument('--top', type=int, default=10, help='Liczba najpopularniejszych słów')
    parser.add_argument('--out', type=str, default='wyniki_rozproszone.json', help='Nazwa pliku wyjściowego')
    
    args = parser.parse_args()
    
    run_distributed(args.data, args.top, args.out)
