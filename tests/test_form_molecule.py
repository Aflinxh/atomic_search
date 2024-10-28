import pytest
import os
import csv
import json
import datetime as dt
import pytz
from atomic_search.atomic_search import form_molecule
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import contextlib
import io

# Function to read the expected atoms and target words from CSV for a given file name
def read_atoms_and_target_words(csv_file_path, file_name):
    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        headers = next(reader).keys()  # Extract the headers as the target words
        target_words = [header for header in headers if header not in ["js_name", "atoms"]]

    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['js_name'].endswith(file_name):
                # Convert the atoms field from JSON string to dictionary
                atoms = json.loads(row['atoms'])
                # Read the expected counts from the CSV for each target_word
                expected_counts = {target_word: int(row[target_word]) for target_word in target_words}
                return atoms, target_words, expected_counts

    return None, None, None

def get_log_dir(log_dir, file_name):
    # Set timezone to Asia/Jakarta
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    time_stamp = dt.datetime.now(jakarta_tz).strftime("%Y-%m-%d_%H-%M-%S")

    # Define the log directory and log file name
    test_log_dir = os.path.join(log_dir, f"test_form_molecule/{time_stamp}_{file_name}")

    return test_log_dir

def save_test_logs(test_log_dir, file_name, errors):
    # Create log file name with timestamp and file name
    log_file_name = f"differences.json"
    log_file_path = os.path.join(test_log_dir, log_file_name)

    # Write errors to JSON log file
    with open(log_file_path, 'w') as log_file:
        json.dump(errors, log_file, indent=4)

    print(f"\nTest failed. Log written to: {log_file_path}")

def log_message(message, test_log_dir):
    log_file_name = f"logs.txt"
    log_file_path = os.path.join(test_log_dir, log_file_name)

    with open(log_file_path, 'a') as log_file:
        log_file.write(message + '\n')

# Test for form_molecule function, either for a specific file or for all files in a directory
def test_form_molecule(file_name, log_dir, dataset_paths, molecule_similarity, expected_mae, expected_r2, show_logs):
    js_folder, csv_file_path = dataset_paths

    y_true = []
    y_pred = []

    if file_name:
        # If a specific file is provided
        js_files = [file_name]
    else:
        # If no specific file is provided, test all JavaScript files in the folder
        js_files = [f for f in os.listdir(js_folder) if f.endswith('.js')]

    # Iterate through each JavaScript file
    for js_file_name in js_files:
        js_file_path = os.path.join(js_folder, js_file_name)

        # Check if the JavaScript file exists
        if not os.path.exists(js_file_path):
            pytest.fail(f"JavaScript file '{js_file_name}' does not exist in the folder '{js_folder}'")

        test_log_dir = get_log_dir(log_dir=log_dir, file_name=js_file_name)
        
        # Store errors for logging purposes
        errors = {}

        # Read atoms and target words from CSV
        atoms, target_words, expected_counts = read_atoms_and_target_words(csv_file_path, js_file_name)

        if atoms is None or target_words is None:
            # Skip if the expected atoms or target words are not found in CSV
            continue

        f = io.StringIO()
        with contextlib.redirect_stdout(f):       
            # Iterate through each target word and run the form_molecule function
            for target_word in target_words:
                # Expected output: the total number of successful molecule combinations for the current target word
                expected_count = expected_counts.get(target_word, 0)
                y_true.append(expected_count)

                # Run the form_molecule function
                result = form_molecule(
                    atoms=atoms,
                    target_word=target_word,
                    molecule_similarity=molecule_similarity.get(target_word),
                    logs=True
                )
                y_pred.append(result)

                # Compare expected vs result for the current target word
                if result != expected_count:
                    # Add the error to the errors dictionary
                    errors[target_word] = {
                        'expected_count': expected_count,
                        'result_count': result
                    }

        # Save logs if there are errors or if --show-logs is enabled
        if errors or show_logs:
            os.makedirs(test_log_dir, exist_ok=True)
            save_test_logs(test_log_dir, js_file_name, errors)
            log_output = f.getvalue()
            log_message(message=log_output, test_log_dir=test_log_dir)

    # Calculate evaluation metrics for all target words across all files
    if len(y_true) == 0 or len(y_pred) == 0:
        pytest.fail("No valid data to compute metrics.")

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    # Print evaluation results for all tested JavaScript files
    if file_name:
        print(f"\nEvaluation Results for file {file_name}:")
    else:
        print(f"\nEvaluation Results for all JavaScript files in the folder:")

    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Mean Squared Error (MSE): {mse:.2f}")
    print(f"R² Score: {r2:.2f}\n")

    # Assert to verify the overall performance
    assert mae <= expected_mae, f"MAE should be less than {expected_mae} for good performance"
    assert r2 >= expected_r2, f"R² should be greater than {expected_r2} to indicate good accuracy"