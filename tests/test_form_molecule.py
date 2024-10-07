import pytest
from atomic_search.atomic_search import form_molecule

def test_form_molecule(common_atoms, molecule_similarity):
    target_word = 'mencarik'

    # Expected output
    expected_count = 2

    # Run the function
    result = form_molecule(atoms=common_atoms, target_word=target_word, molecule_similarity=molecule_similarity, debugging=False)

    # Check if the result matches the expected output
    assert result == expected_count, f"Expected {expected_count}, but got {result}"
