import os
import sys

# Dodanie ścieżki do importów
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.seq_baseline import process_directory

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
    
    counts, total_words = process_directory(test_dir)
    
    assert total_words == 10, f"Oczekiwano 10 słów, otrzymano {total_words}"
    assert len(counts) == 5, f"Oczekiwano 5 unikalnych słów, otrzymano {len(counts)}"
    
    assert counts["a"] == 2
    assert counts["b"] == 2
    assert counts["c"] == 2
    assert counts["d"] == 2
    assert counts["e"] == 2
    
    print("Test poprawności sekwencyjnego zliczania zakończony sukcesem!")
    print(f"Zliczone słowa: {total_words}")
    print(f"Klucze: {dict(counts)}")

if __name__ == "__main__":
    test_baseline_correctness()
