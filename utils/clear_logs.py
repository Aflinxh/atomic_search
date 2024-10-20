import shutil
import os

def clear_logs():
    if os.path.exists("logs/test_extract_atoms"):
        shutil.rmtree("logs/test_extract_atoms")
    if os.path.exists("logs/test_form_molecule"):
        shutil.rmtree("logs/test_form_molecule")
    if os.path.exists("logs/test_atomic_search"):
        shutil.rmtree("logs/test_atomic_search")
    os.makedirs("logs/test_extract_atoms", exist_ok=True)
    os.makedirs("logs/test_form_molecule", exist_ok=True)
    os.makedirs("logs/test_atomic_search", exist_ok=True)

if __name__ == "__main__":
    clear_logs()
