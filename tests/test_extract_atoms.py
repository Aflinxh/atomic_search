import pytest
import os
import csv
import json
from atomic_search.atomic_search import extract_atoms
from conftest import save_test_logs  # Import save_test_logs at the top

# Fixture to prepare dataset paths and expected atoms from CSV
@pytest.fixture
def dataset_paths():
    js_folder = 'dataset-testing/js'
    csv_file_path = 'dataset-testing/obfuscated_js_dataset.csv'
    return js_folder, csv_file_path

# Function to read the expected atoms from CSV
def read_expected_atoms(csv_file_path, file_name):
    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['js_name'].endswith(file_name):
                # Convert the atoms field from JSON string to dictionary
                expected_atoms = json.loads(row['atoms'])
                return expected_atoms
    return None

# Function to filter atoms to only compare value and ref properties
def filter_atoms(atoms):
    filtered_atoms = {}
    for key, atom_list in atoms.items():
        filtered_atoms[key] = [{'value': atom['value'], 'ref': atom['ref']} for atom in atom_list]
    return filtered_atoms

# Function to find the difference between two lists of atoms
def compare_atoms(filtered_result, filtered_expected):
    result_diff = {}
    for key in filtered_expected.keys():
        expected_set = set(tuple(atom.items()) for atom in filtered_expected[key])
        result_set = set(tuple(atom.items()) for atom in filtered_result.get(key, []))

        # Atoms in expected but not in result (missing atoms)
        missing_atoms = expected_set - result_set
        # Atoms in result but not in expected (extra atoms)
        extra_atoms = result_set - expected_set

        if missing_atoms or extra_atoms:
            result_diff[key] = {
                'missing_atoms': [dict(atom) for atom in missing_atoms],
                'extra_atoms': [dict(atom) for atom in extra_atoms]
            }

    return result_diff

# Test for extract_atoms with flexibility for either hardcoded input or dynamic file input
def test_extract_atoms(file_name, log_dir, dataset_paths):
    if file_name is None:
        # Use hardcoded input for the test case
        target_words = ["mencarik", "test", "apa"]
        search_space = "men+rik++ca:/++nc+++,nk+mend++a++m++td++e+ar+nc+i+k+a+st+pa+te+cd+stt+aa+pa+a+pa"
        min_atom_size = 1

        # Expected result for the hardcoded test case
        common_atoms = {
            'mencarik': [
                {'value': 'men', 'ref': 'mencarik'},
                {'value': 'rik', 'ref': 'mencarik'},
                {'value': 'ca', 'ref': 'mencarik'},
                {'value': 'nc', 'ref': 'mencarik'},
                {'value': 'm', 'ref': 'mencarik'},
                {'value': 'ar', 'ref': 'mencarik'},
                {'value': 'nc', 'ref': 'mencarik'},
                {'value': 'i', 'ref': 'mencarik'},
                {'value': 'k', 'ref': 'mencarik'}
            ],
            'ambiguous_word': [
                {'value': 'a', 'ref': 'ambiguous_word'},
                {'value': 'e', 'ref': 'ambiguous_word'},
                {'value': 'a', 'ref': 'ambiguous_word'},
                {'value': 'a', 'ref': 'ambiguous_word'}
            ],
            'test': [
                {'value': 'st', 'ref': 'test'},
                {'value': 'te', 'ref': 'test'}
            ],
            'apa': [
                {'value': 'pa', 'ref': 'apa'},
                {'value': 'pa', 'ref': 'apa'},
                {'value': 'pa', 'ref': 'apa'}
            ]
        }

        # Run the function
        result = extract_atoms(target_words, search_space, min_atom_size)

        # Filter the result and expected atoms to only compare value and ref properties
        filtered_result = filter_atoms(result)
        filtered_expected = filter_atoms(common_atoms)

        # Compare atoms to find any differences
        differences = compare_atoms(filtered_result, filtered_expected)

        # Write logs only if test fails
        if differences:
            save_test_logs('test_extract_atoms', log_dir, filtered_result, filtered_expected, differences)
            pytest.fail(f"Extracted atoms differ from expected atoms. Check logs for details.")

    else:
        # If file name is provided, use its content and CSV data
        js_folder, csv_file_path = dataset_paths
        js_file_path = os.path.join(js_folder, file_name)

        # Check if the JavaScript file exists
        if not os.path.exists(js_file_path):
            pytest.fail(f"JavaScript file '{file_name}' does not exist in the folder '{js_folder}'")

        # Read the JavaScript file content
        with open(js_file_path, 'r') as file:
            search_space = file.read()

        # Read the expected atoms from the CSV
        expected_atoms = read_expected_atoms(csv_file_path, file_name)
        if expected_atoms is None:
            pytest.fail(f"Expected atoms for file '{file_name}' not found in '{csv_file_path}'")

        # Use the target words from the keys of expected atoms
        target_words = list(expected_atoms.keys())
        min_atom_size = 1

        # Run the function
        result = extract_atoms(target_words, search_space, min_atom_size)

        # Filter the result and expected atoms to only compare value and ref properties
        filtered_result = filter_atoms(result)
        filtered_expected = filter_atoms(expected_atoms)

        # Compare atoms to find any differences
        differences = compare_atoms(filtered_result, filtered_expected)

        # Write logs only if test fails
        if differences:
            save_test_logs('test_extract_atoms', log_dir, filtered_result, filtered_expected, differences)
            pytest.fail(f"Extracted atoms differ from expected atoms. Check logs for details.")
