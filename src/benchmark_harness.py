import os
import sys
import time
import multiprocessing

# Dodanie ścieżki do importu z src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.seq_baseline import run_baseline
from src.parallel_mvp import run_parallel

def run_benchmark():
    data_dir = os.path.join(parent_dir, "data")
    
    if not os.path.exists(data_dir):
        print(f"Katalog z danymi {data_dir} nie istnieje. Upewnij się, że dane są dostępne.")
        return
        
    print(f"=== URUCHAMIANIE BENCHMARKU DLA ZBIORU {data_dir} ===")
    
    # Baseline Sekwencyjny
    print("\n--- TEST: Wersja Sekwencyjna (Baseline) ---")
    start_time = time.time()
    results_seq = run_baseline(data_dir, output_file=os.path.join(parent_dir, "wyniki_sekwencyjne.json"))
    end_time = time.time()
    real_execution_time_seq = end_time - start_time
    print(f"Mierzony czas w uprzęży pomiarowej względem całego wywołania run_baseline: {real_execution_time_seq:.4f} s")
    
    max_cores = multiprocessing.cpu_count()
    
    # Równoległy C1 (2 workery)
    print("\n--- TEST: Wersja Równoległa C1 (2 Workery) ---")
    start_time = time.time()
    run_parallel(data_dir, max_workers=2, output_file=os.path.join(parent_dir, "wyniki_rownolegle_C1.json"))
    end_time = time.time()
    print(f"Czas uprzęży (C1): {end_time - start_time:.4f} s")
    
    # Równoległy C2 (4 workery)
    print("\n--- TEST: Wersja Równoległa C2 (4 Workery) ---")
    start_time = time.time()
    run_parallel(data_dir, max_workers=4, output_file=os.path.join(parent_dir, "wyniki_rownolegle_C2.json"))
    end_time = time.time()
    print(f"Czas uprzęży (C2): {end_time - start_time:.4f} s")
    
    # Równoległy C3 (max workery)
    print(f"\n--- TEST: Wersja Równoległa C3 ({max_cores} Workerów - Max) ---")
    start_time = time.time()
    run_parallel(data_dir, max_workers=max_cores, output_file=os.path.join(parent_dir, "wyniki_rownolegle_C3.json"))
    end_time = time.time()
    print(f"Czas uprzęży (C3): {end_time - start_time:.4f} s")
    
    # Import dla symulacji rozproszonej
    from src.distributed_master import run_distributed
    from src.distributed_worker import run_worker
    
    def run_distributed_benchmark(name, num_workers, out_file):
        print(f"\n--- TEST: Wersja Rozproszona {name} ({num_workers} Workery) ---")
        workers = []
        for _ in range(num_workers):
            p = multiprocessing.Process(target=run_worker, kwargs={"address": ('127.0.0.1', 50000)})
            p.daemon = True
            p.start()
            workers.append(p)
            
        start_time = time.time()
        run_distributed(data_dir, output_file=out_file)
        end_time = time.time()
        
        # czekamy az workery sie wyłącza po odebraniu sygnalu stopu
        for p in workers:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
        
        print(f"Czas uprzęży (Rozproszona {name}): {end_time - start_time:.4f} s")

    # Rozproszony C1
    run_distributed_benchmark("C1", 2, os.path.join(parent_dir, "wyniki_rozproszone_C1.json"))
    
    # Opóźnienie zapobiegające błędowi "Address already in use".
    # Dajemy systemowi operacyjnemu (stan TIME_WAIT) chwilę na zwolnienie gniazda TCP (portu 50000) przed ponownym startem Mastera.
    time.sleep(2)
    
    # Rozproszony C2
    run_distributed_benchmark("C2", 4, os.path.join(parent_dir, "wyniki_rozproszone_C2.json"))
    
if __name__ == "__main__":
    # wymagane na Windowsie przy uzyciu multiprocessing
    run_benchmark()
