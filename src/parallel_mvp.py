import os
import glob
import time
import json
import concurrent.futures
from collections import Counter

# Dodanie ścieżki do importu z src dla process_file
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.seq_baseline import process_file

def process_directory_parallel(directory_path, file_pattern="*.txt", max_workers=None):
    """Przetwarza pliki w katalogu równolegle przy użyciu puli procesów."""
    files = glob.glob(os.path.join(directory_path, file_pattern))
    if not files:
        print(f"Brak plików {file_pattern} w ścieżce {directory_path}")
        return Counter(), 0, 0.0, 0.0
        
    total_word_counts = Counter()
    total_words = 0
    total_io_time = 0.0
    total_cpu_time = 0.0
    
    # Rozpoczęcie mapowania zadań na workery. 
    # W środowisku Windows (używa logiki spawn) bezpiecznie dziedziczy referencje jeśli są we właściwie zabezpieczonych modułach.
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # executor.map automatycznie dzieli iterator iterowalnej kolekcji na batche i nadzoruje ich ukończenie
        results = executor.map(process_file, files)
        
        # Agregacja w Wątku Głównym (Parent Process)
        for counts, words, io_time, cpu_time in results:
            total_word_counts.update(counts)
            total_words += words
            total_io_time += io_time
            total_cpu_time += cpu_time
            
    return total_word_counts, total_words, total_io_time, total_cpu_time

def run_parallel(directory_path, max_workers=None, top_n=10, output_file="wyniki_rownolegle.json"):
    workers_str = str(max_workers) if max_workers else "AUTO (wszystkie rdzenie)"
    print(f"Rozpoczęcie przetwarzania równoległego dla katalogu: {directory_path} (Workery: {workers_str}) ...")
    start_time = time.perf_counter()
    
    word_counts, total_words, total_io_time, total_cpu_time = process_directory_parallel(
        directory_path, 
        max_workers=max_workers
    )
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    top_words = word_counts.most_common(top_n)
    unique_words = len(word_counts)
    
    results = {
        "metoda": "rownolegla",
        "liczba_workerow": workers_str,
        "katalog": directory_path,
        "calkowita_liczba_slow": total_words,
        "liczba_unikalnych_slow": unique_words,
        "top_slowa": top_words,
        "czas_io_sekundy_zsumowany": total_io_time, 
        "czas_cpu_sekundy_zsumowany": total_cpu_time, 
        "czas_wykonania_sekundy": execution_time
    }
    
    print("\n--- Podsumowanie (Równoległe) ---")
    print(f"Liczba workerów: {workers_str}")
    print(f"Całkowita liczba słów: {total_words}")
    print(f"Liczba unikalnych słów: {unique_words}")
    print(f"Top {top_n} najczęstszych słów:")
    for word, count in top_words:
        print(f"  {word}: {count}")
    print(f"\nZsumowany czas I/O (narzut dyskowy wielu procesów): {total_io_time:.4f} s")
    print(f"Zsumowany czas CPU (praca wszystkich procesów): {total_cpu_time:.4f} s")
    print(f"Rzeczywisty czas trwania (Wall-clock Time): {execution_time:.4f} s\n")

    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Równoległe przetwarzanie plików tekstowych.')
    parser.add_argument('--data', type=str, default='data', help='Ścieżka do folderu z danymi')
    parser.add_argument('--workers', type=int, default=None, help='Liczba workerów (domyślnie wszystkie rdzenie)')
    parser.add_argument('--top', type=int, default=10, help='Liczba najpopularniejszych słów')
    parser.add_argument('--out', type=str, default='wyniki_rownolegle.json', help='Nazwa pliku wyjściowego')
    
    args = parser.parse_args()
    run_parallel(args.data, args.workers, args.top, args.out)
