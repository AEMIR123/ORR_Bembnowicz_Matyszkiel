import time
import string
from collections import Counter
from multiprocessing.managers import BaseManager
import queue

class QueueManager(BaseManager):
    pass

# Tabela translacji (identyczna do sekwencyjnego)
translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))

def process_text_chunk(text_chunk):
    """Zlicza slowa w otrzymanym bloku tekstu."""
    t_cpu_start = time.perf_counter()
    
    clean_line = text_chunk.translate(translator).lower()
    words = clean_line.split()
    
    word_counts = Counter(words)
    total_words = len(words)
    
    cpu_time = time.perf_counter() - t_cpu_start
    
    return word_counts, total_words, cpu_time

def run_worker(address=('localhost', 50000), authkey=b'orr_secret'):
    QueueManager.register('get_task_queue')
    QueueManager.register('get_result_queue')
    
    print(f"Próba połączenia z głównym serwerem pod adresem {address}...")
    
    manager = QueueManager(address=address, authkey=authkey)
    
    connected = False
    for _ in range(10): # 10 retries
        try:
            manager.connect()
            print("Połączenie udane. Worker nasłuchuje na wezwania...")
            connected = True
            break
        except ConnectionRefusedError:
            print("Brak połączenia. Próbowanie ponownie za sekundę...")
            time.sleep(1)
            
    if not connected:
        print("Brak połączenia pomimo prób. Zamykanie workera.")
        return

    task_queue = manager.get_task_queue()
    result_queue = manager.get_result_queue()
    
    tasks_processed = 0
    total_cpu_time = 0.0
    
    while True:
        try:
            # timeout zeby nie zablokować wątku na zawsze jak kolejka jest pusta
            task_chunk = task_queue.get(timeout=3.0)
        except queue.Empty:
            continue
        except (ConnectionResetError, EOFError, BrokenPipeError):
            print("Serwer zakończył pracę. Wypisywanie się pracownika z sieci.")
            break
            
        if task_chunk is None:
            print("Otrzymano znak stopu 'Poison Pill'. Wypisywanie się pracownika z sieci koordynatora.")
            # przekazujemy None dalej żeby reszta workerów też mogła skończyć
            try:
                task_queue.put(None)
            except (ConnectionResetError, EOFError, BrokenPipeError):
                pass  # master już zamknął manager
            break
            
        counts, words, cpu_t = process_text_chunk(task_chunk)
        
        # odsyłamy wynik do mastera
        result_queue.put((counts, words, cpu_t))
        
        tasks_processed += 1
        total_cpu_time += cpu_t
        
    print(f"Worker konczy prace. Zadania: {tasks_processed}, czas CPU: {total_cpu_time:.4f}s")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Odbiorca rozproszony z zadań (Worker).')
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='Adres IP serwera (Mastera)')
    parser.add_argument('--port', type=int, default=50000, help='Port serwera (Mastera)')
    
    args = parser.parse_args()
    run_worker(address=(args.ip, args.port))
