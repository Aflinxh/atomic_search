import pytest
from atomic_search.atomic_search import extract_atoms

def test_extract_atoms(common_atoms, min_atom_size):
    # Test input and expected output
    target_words = ["mencarik", "test", "apa"]
    search_space = "men+rik++ca:/++nc+++,nk+mend++a++m++td++e+ar+nc+i+k+a+st+pa+te+cd+stt+aa+pa+a+pa"

    # Run the function
    result = extract_atoms(target_words, search_space, min_atom_size)

    # Check if the result matches the expected output
    assert result == common_atoms, f"Expected {common_atoms}, but got {result}"

# If you want to run this test alone using pytest, add the following lines:
if __name__ == "__main__":
    pytest.main([__file__])
