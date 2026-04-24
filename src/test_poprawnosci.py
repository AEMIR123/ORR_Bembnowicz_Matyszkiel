import os
import sys

# Dodanie ścieżki do importów
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.seq_baseline import process_directory as process_directory_seq
from src.parallel_mvp import process_directory_parallel

from src.distributed_master import process_directory_distributed
from src.distributed_worker import run_worker
import threading
import time

def setup_test_data(test_dir):
    os.makedirs(test_dir, exist_ok=True)
    with open(os.path.join(test_dir, "plik1.txt"), "w", encoding="utf-8") as f:
        f.write("A B C A C D\n")
        
    with open(os.path.join(test_dir, "plik2.txt"), "w", encoding="utf-8") as f:
        f.write("B D E E\n")

def test_baseline_correctness():
    test_dir = os.path.join(parent_dir, "test_data")
    setup_test_data(test_dir)
    print(f"Wygenerowano dane testowe w {test_dir}\n")
    
    print("--- Testowanie Logiki Sekwencyjnej (Baseline) ---")
    counts_seq, total_words_seq, _, _ = process_directory_seq(test_dir)
    
    assert total_words_seq == 10, f"Oczekiwano 10 słów, otrzymano {total_words_seq}"
    assert len(counts_seq) == 5, f"Oczekiwano 5 unikalnych słów, otrzymano {len(counts_seq)}"
    assert counts_seq["a"] == 2
    assert counts_seq["b"] == 2
    assert counts_seq["c"] == 2
    assert counts_seq["d"] == 2
    assert counts_seq["e"] == 2
    
    print("--- Testowanie Logiki Równoległej (Parallel) ---")
    counts_par, total_words_par, _, _ = process_directory_parallel(test_dir, max_workers=2)
    
    assert total_words_seq == total_words_par, "Błąd liczby słów (seq != par)"
    assert counts_seq == counts_par, "Błąd stanu wyników Counter() (seq != par)"
    print("[OK] Test poprawności MVP Parallel względem Baseline zakończony sukcesem!\n")
    
    print("--- Testowanie Logiki Rozproszonej (Distributed) ---")
    # Otwórz węzeł uderzający po Localhoście:
    # Serwer stworzony zostanie podczas wywołania funkcji rozproszonej
    # Ale workera puszczamy teraz w tle
    worker_t = threading.Thread(target=run_worker, kwargs={"address": ('127.0.0.1', 50000)}, daemon=True)
    worker_t.start()
    
    counts_dist, total_words_dist, _, _ = process_directory_distributed(test_dir, address=('127.0.0.1', 50000))
    
    assert total_words_seq == total_words_dist, "Błąd liczby słów (seq != dist)"
    assert counts_seq == counts_dist, "Błąd stanu wyników Counter() (seq != dist)"

    print("\n[OK] Test poprawności MVP Rozproszonego (Distributed) względem Baseline zakończony sukcesem!")
    print(f"Zliczone słowa całkowite: {total_words_dist}")
    print(f"Klucze: {dict(counts_dist)}")

if __name__ == "__main__":
    # Ochrona w procesie głównym na Windowsie dla ProcessPoolExecutor
    test_baseline_correctness()
