import pytest
import os
import csv
import json
from atomic_search.atomic_search import extract_atoms
from conftest import save_test_logs
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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

def test_extract_atoms(file_name, log_dir, dataset_paths, expected_mae, expected_r2):
    js_folder, csv_file_path = dataset_paths

    y_true = []
    y_pred = []

    if file_name:
        # If file name is provided, use its content and CSV data
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

        # Write logs if differences are found
        if differences:
            save_test_logs('test_extract_atoms', log_dir, filtered_result, filtered_expected, differences)

        # Prepare y_true and y_pred for regression metrics
        for key in filtered_expected.keys():
            y_true.append(len(filtered_expected[key]))
            y_pred.append(len(filtered_result.get(key, [])))

        # Calculate evaluation metrics for the current file
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # Print evaluation results for the current file
        print(f"\nEvaluation Results for file {file_name}:")
        print(f"Mean Absolute Error (MAE): {mae:.2f}")
        print(f"Mean Squared Error (MSE): {mse:.2f}")
        print(f"R² Score: {r2:.2f}\n")

        assert mae <= expected_mae, f"MAE for file '{file_name}' should be less than {expected_mae}"
        assert r2 >= expected_r2, f"R² for file '{file_name}' should be greater than {expected_r2} to indicate good accuracy"

    else:
        # If no specific file is provided, test all JavaScript files in the folder
        js_files = [f for f in os.listdir(js_folder) if f.endswith('.js')]

        # Iterate through each JavaScript file in the folder
        for js_file_name in js_files:
            js_file_path = os.path.join(js_folder, js_file_name)

            # Read JavaScript file content
            with open(js_file_path, 'r') as file:
                search_space = file.read()

            # Read the expected atoms from the CSV
            expected_atoms = read_expected_atoms(csv_file_path, js_file_name)
            if expected_atoms is None:
                # Skip if the expected atoms are not found in CSV
                continue

            # Use the target words from the keys of expected atoms
            target_words = list(expected_atoms.keys())
            min_atom_size = 1

            # Run the extract_atoms function
            result = extract_atoms(target_words, search_space, min_atom_size)

            # Filter the result and expected atoms to only compare value and ref properties
            filtered_result = filter_atoms(result)
            filtered_expected = filter_atoms(expected_atoms)

            # Compare atoms to find any differences
            differences = compare_atoms(filtered_result, filtered_expected)

            # Write logs if differences are found
            if differences:
                save_test_logs(f'test_extract_atoms_{js_file_name}', log_dir, filtered_result, filtered_expected, differences)

            # Prepare y_true and y_pred for regression metrics
            for key in filtered_expected.keys():
                y_true.append(len(filtered_expected[key]))
                y_pred.append(len(filtered_result.get(key, [])))

        # Calculate evaluation metrics for all files
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # Print evaluation results for all JavaScript files
        print(f"\nEvaluation Results for all JavaScript files in the folder:")
        print(f"Mean Absolute Error (MAE): {mae:.2f}")
        print(f"Mean Squared Error (MSE): {mse:.2f}")
        print(f"R² Score: {r2:.2f}\n")

        assert mae <= expected_mae, f"MAE should be less than {expected_mae} for good performance"
        assert r2 >= expected_r2, f"R² should be greater than {expected_r2} to indicate good accuracy"