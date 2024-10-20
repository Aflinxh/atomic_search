import pytest
import os
import csv
import json
import datetime as dt
import pytz
from atomic_search.atomic_search import extract_atoms
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
        filtered_atoms[key] = [{'value': atom['value'], 'ref': atom['ref']} for atom in atom_list] if atom_list else []
    return filtered_atoms

# Function to find the difference between two lists of atoms
def compare_atoms(filtered_result, filtered_expected):
    result_diff = {}

    # Loop through each key in filtered_expected
    for key in filtered_expected.keys():
        expected_atoms = filtered_expected[key]
        result_atoms = filtered_result.get(key, [])

        # Check if the key is missing in the result
        if key not in filtered_result:
            result_diff[key] = {
                'missing_atoms': expected_atoms,  # All expected atoms are missing if the key is not present
                'extra_atoms': [],  # No extra atoms since the key is missing
                'message': 'This key is missing'
            }
            continue

        # Mark all atoms in result_atoms as unused initially
        for atom in result_atoms:
            atom['used'] = False

        missing_atoms = []
        extra_atoms = []

        # Compare expected atoms to result atoms
        for expected_atom in expected_atoms:
            found = False
            for result_atom in result_atoms:
                # Check if atom hasn't been used and matches 'value' and 'ref'
                if not result_atom['used'] and result_atom['value'] == expected_atom['value'] and result_atom['ref'] == expected_atom['ref']:
                    result_atom['used'] = True  # Mark the result atom as used
                    found = True
                    break
            if not found:
                # If no matching atom is found, add to missing_atoms
                missing_atoms.append(expected_atom)

        # After checking all expected atoms, find extra unused atoms in result_atoms
        for result_atom in result_atoms:
            if not result_atom['used']:
                extra_atoms.append({k: result_atom[k] for k in ('value', 'ref')})  # Include only 'value' and 'ref' in extra_atoms

        # If there are missing or extra atoms, add them to result_diff
        if missing_atoms or extra_atoms:
            result_diff[key] = {
                'missing_atoms': missing_atoms,
                'extra_atoms': extra_atoms
            }

    return result_diff

# Update the save_test_logs function to handle differences
def save_test_logs(test_name, file_name, log_dir, filtered_result, filtered_expected, differences):
    jakarta_tz = pytz.timezone('Asia/Jakarta')

    # Create the folder structure for logs
    time_stamp = dt.datetime.now(jakarta_tz).strftime("%Y-%m-%d_%H-%M-%S")
    test_log_dir = os.path.join(log_dir, f"{test_name}/{time_stamp}_{file_name}")
    os.makedirs(test_log_dir, exist_ok=True)

    # Write filtered result, expected and differences to separate log files
    result_file = os.path.join(test_log_dir, 'filtered_result.json')
    expected_file = os.path.join(test_log_dir, 'filtered_expected.json')
    differences_file = os.path.join(test_log_dir, 'differences.json')

    with open(result_file, 'w') as f:
        json.dump(filtered_result, f, indent=4)
    with open(expected_file, 'w') as f:
        json.dump(filtered_expected, f, indent=4)
    with open(differences_file, 'w') as f:
        json.dump(differences, f, indent=4)

    print(f"\nTest failed. Logs written to: {test_log_dir}")

# Function to evaluate atoms extraction for a given JavaScript file
def evaluate_atoms(file_name, search_space, expected_atoms, log_dir, show_logs):
    # Use the target words from the keys of expected atoms
    target_words = [key for key in expected_atoms.keys() if key != "ambiguous_word"]

    min_atom_size = 1

    # Run the extract_atoms function
    result = extract_atoms(target_words, search_space, min_atom_size)

    # Filter the result and expected atoms to only compare value and ref properties
    filtered_result = filter_atoms(result)
    filtered_expected = filter_atoms(expected_atoms)

    # Compare atoms to find any differences
    differences = compare_atoms(filtered_result, filtered_expected)

    # Write logs if differences are found or show_logs is True
    if differences or show_logs:
        save_test_logs('test_extract_atoms', file_name, log_dir, filtered_result, filtered_expected, differences)

    # Prepare y_true and y_pred for regression metrics
    y_true = []
    y_pred = []
    for key in filtered_expected.keys():
        y_true.append(len(filtered_expected[key]))
        y_pred.append(len(filtered_result.get(key, [])))

    return y_true, y_pred

# Main test function for extract_atoms
def test_extract_atoms(file_name, log_dir, dataset_paths, expected_mae, expected_r2, show_logs):
    js_folder, csv_file_path = dataset_paths

    y_true_total = []
    y_pred_total = []

    if file_name:
        # Test a specific file if provided
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

        # Evaluate atoms for the given file
        y_true, y_pred = evaluate_atoms(file_name, search_space, expected_atoms, log_dir, show_logs)
        y_true_total.extend(y_true)
        y_pred_total.extend(y_pred)

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

            # Evaluate atoms for the given file
            y_true, y_pred = evaluate_atoms(js_file_name, search_space, expected_atoms, log_dir, show_logs)
            y_true_total.extend(y_true)
            y_pred_total.extend(y_pred)

    # Calculate evaluation metrics for all files
    if len(y_true_total) == 0 or len(y_pred_total) == 0:
        pytest.fail("No valid data to compute metrics.")

    mae = mean_absolute_error(y_true_total, y_pred_total)
    mse = mean_squared_error(y_true_total, y_pred_total)
    r2 = r2_score(y_true_total, y_pred_total)

    # Print evaluation results
    if file_name:
        print(f"\nEvaluation Results for file {file_name}:")
    else:
        print(f"\nEvaluation Results for all JavaScript files in the folder:")

    print(f"True Values: {y_true_total}")
    print(f"Predicted Values: {y_pred_total}")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Mean Squared Error (MSE): {mse:.2f}")
    print(f"R² Score: {r2:.2f}\n")

    # Assert to verify the overall performance
    assert mae <= expected_mae, f"MAE should be less than {expected_mae} for good performance"
    assert r2 >= expected_r2, f"R² should be greater than {expected_r2} to indicate good accuracy"