from .extract_atoms import extract_atoms
from .form_molecule import form_molecule

def atomic_search(target_words, search_space, min_atom_size, molecule_similarity, logs=False):
    atoms = extract_atoms(target_words, search_space, min_atom_size)

    results = {}
    for target_word in target_words:
        if logs:
            print(f"\n{atoms}")
            print(f"--- Target: {target_word}\n")
        result = form_molecule(atoms, target_word, molecule_similarity.get(target_word, "100%"), logs)
        results[target_word] = result

    if logs:
        print(f"{atoms}\n")
        
    return results