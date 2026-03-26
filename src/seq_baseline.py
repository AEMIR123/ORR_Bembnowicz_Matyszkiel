import os
import glob
import time
import json
import string
from collections import Counter

# Tabela translacji do zamiany znaków interpunkcyjnych na spacje
translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))

def process_file(filepath):
    """Processes a single text file and returns word counts and total words."""
    word_counts = Counter()
    total_words = 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Podmień znaki interpunkcyjne/specjalne na spacje, a potem znormalizuj by wszystkie były z małej litery
            clean_line = line.translate(translator).lower()
            
            words = clean_line.split()
            word_counts.update(words)
            total_words += len(words)
    return word_counts, total_words

def process_directory(directory_path, file_pattern="*.txt"):
    """Processes all files in a directory sequentially."""
    files = glob.glob(os.path.join(directory_path, file_pattern))
    if not files:
        print(f"Brak plików {file_pattern} w ścieżce {directory_path}")
        return Counter(), 0
        
    total_word_counts = Counter()
    total_words = 0
    
    for filepath in files:
        counts, words = process_file(filepath)
        total_word_counts.update(counts)
        total_words += words
        
    return total_word_counts, total_words

def run_baseline(directory_path, top_n=10, output_file="wyniki.json"):
    print(f"Rozpoczęcie przetwarzania sekwencyjnego dla katalogu: {directory_path} ...")
    start_time = time.time()
    
    word_counts, total_words = process_directory(directory_path)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    top_words = word_counts.most_common(top_n)
    unique_words = len(word_counts)
    
    results = {
        "metoda": "sekwencyjna",
        "katalog": directory_path,
        "calkowita_liczba_slow": total_words,
        "liczba_unikalnych_slow": unique_words,
        "top_slowa": top_words,
        "czas_wykonania_sekundy": execution_time
    }
    
    print("\n--- Podsumowanie (Sekwencyjnie) ---")
    print(f"Całkowita liczba słów: {total_words}")
    print(f"Liczba unikalnych słów: {unique_words}")
    print(f"Top {top_n} najczęstszych słów:")
    for word, count in top_words:
        print(f"  {word}: {count}")
    print(f"Czas wykonania: {execution_time:.4f} s\n")

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
