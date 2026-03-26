import os
import sys
import time

# Dodanie ścieżki do importu z src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.seq_baseline import run_baseline

def run_benchmark():
    data_dir = os.path.join(parent_dir, "data")
    
    if not os.path.exists(data_dir):
        print(f"Katalog z danymi {data_dir} nie istnieje. Upewnij się, że dane są dostępne.")
        return
        
    print(f"=== URUCHAMIANIE BENCHMARKU DLA ZBIORU {data_dir} ===")
    
    # Baseline Sekwencyjny
    print("\n--- TEST: Wersja Sekwencyjna (Baseline) ---")
    
    start_time = time.time()
    results = run_baseline(data_dir, output_file=os.path.join(parent_dir, "wyniki_sekwencyjne.json"))
    end_time = time.time()
    
    real_execution_time = end_time - start_time
    
    print("\nZakończono Benchmark Sekwencyjny.")
    print(f"Mierzony czas w uprzęży pomiarowej względem całego wywołania run_baseline: {real_execution_time:.4f} s")
    
if __name__ == "__main__":
    run_benchmark()
