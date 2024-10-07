from .extract_atoms import extract_atoms
from .form_molecule import form_molecule

def atomic_search(target_words, search_space, min_atom_size, molecule_similarity, debugging=False):
    atoms = extract_atoms(target_words, search_space, min_atom_size)

    results = {}
    for target_word in target_words:
        if debugging:
            print(f"\n{atoms}")
            print(f"--- Target: {target_word}\n")
        result = form_molecule(atoms, target_word, molecule_similarity, debugging)
        results[target_word] = result

    if debugging:
        print(f"{atoms}\n")
        
    return results