import os
import glob
import time
import json
import string
from collections import Counter

# Tabela translacji do zamiany znaków interpunkcyjnych na spacje
translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))

def process_file(filepath):
    """Przetwarza pojedynczy plik tekstowy i zwraca zliczone słowa, całkowitą liczbę słów, czas I/O i czas CPU."""
    word_counts = Counter()
    total_words = 0
    io_time_total = 0.0
    cpu_time_total = 0.0
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        while True:
            # Pomiar czasu I/O (odczyt z dysku)
            t_io_start = time.perf_counter()
            line = f.readline()
            io_time_total += (time.perf_counter() - t_io_start)
            
            if not line:
                break
            
            # Pomiar czasu CPU (przetwarzanie tekstu)
            t_cpu_start = time.perf_counter()
            clean_line = line.translate(translator).lower()
            words = clean_line.split()
            word_counts.update(words)
            total_words += len(words)
            cpu_time_total += (time.perf_counter() - t_cpu_start)
            
    return word_counts, total_words, io_time_total, cpu_time_total

def process_directory(directory_path, file_pattern="*.txt"):
    """Przetwarza sekwencyjnie wszystkie pliki w podanym katalogu."""
    files = glob.glob(os.path.join(directory_path, file_pattern))
    if not files:
        print(f"Brak plików {file_pattern} w ścieżce {directory_path}")
        return Counter(), 0, 0.0, 0.0
        
    total_word_counts = Counter()
    total_words = 0
    total_io_time = 0.0
    total_cpu_time = 0.0
    
    for filepath in files:
        counts, words, io_time, cpu_time = process_file(filepath)
        total_word_counts.update(counts)
        total_words += words
        total_io_time += io_time
        total_cpu_time += cpu_time
        
    return total_word_counts, total_words, total_io_time, total_cpu_time

def run_baseline(directory_path, top_n=10, output_file="wyniki.json"):
    print(f"Rozpoczęcie przetwarzania sekwencyjnego dla katalogu: {directory_path} ...")
    start_time = time.perf_counter()
    
    word_counts, total_words, total_io_time, total_cpu_time = process_directory(directory_path)
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    top_words = word_counts.most_common(top_n)
    unique_words = len(word_counts)
    
    results = {
        "metoda": "sekwencyjna",
        "katalog": directory_path,
        "calkowita_liczba_slow": total_words,
        "liczba_unikalnych_slow": unique_words,
        "top_slowa": top_words,
        "czas_io_sekundy": total_io_time,
        "czas_cpu_sekundy": total_cpu_time,
        "czas_wykonania_sekundy": execution_time
    }
    
    print("\n--- Podsumowanie (Sekwencyjnie) ---")
    print(f"Całkowita liczba słów: {total_words}")
    print(f"Liczba unikalnych słów: {unique_words}")
    print(f"Top {top_n} najczęstszych słów:")
    for word, count in top_words:
        print(f"  {word}: {count}")
    print(f"\nCzas I/O (Dysk): {total_io_time:.4f} s")
    print(f"Czas CPU (Parsowanie): {total_cpu_time:.4f} s")
    print(f"Czas wykonania całkowity: {execution_time:.4f} s\n")

    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"Wyniki zapisano do {output_file}")
        
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Sekwencyjne przetwarzanie plików tekstowych.')
    parser.add_argument('--data', type=str, default='data', help='Ścieżka do folderu z danymi')
    parser.add_argument('--top', type=int, default=10, help='Liczba najpopularniejszych słów')
    parser.add_argument('--out', type=str, default='wyniki.json', help='Nazwa pliku wyjściowego')
    
    args = parser.parse_args()
    run_baseline(args.data, args.top, args.out)
