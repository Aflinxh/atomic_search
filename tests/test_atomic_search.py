import os
import pytest
from atomic_search import atomic_search
import csv
import io
import contextlib
import datetime as dt
import pytz
import json
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Function to read the expected counts from the CSV file
def read_expected_counts(csv_file_path, file_name):
    results = {}

    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            if row['js_name'].endswith(file_name):
                for key, value in row.items():
                    if key not in ['js_name', 'atoms']:
                        results[key] = int(value)
                break

    return results

# Function to get the log directory
def get_log_dir(log_dir, file_name):
    # Set timezone to Asia/Jakarta
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    time_stamp = dt.datetime.now(jakarta_tz).strftime("%Y-%m-%d_%H-%M-%S")

    # Define the log directory and log file name
    test_log_dir = os.path.join(log_dir, f"test_atomic_search/{time_stamp}_{file_name}")

    return test_log_dir

# Function to save test logs in JSON format
def save_test_logs(test_log_dir, file_name, errors):
    # Create log file name with timestamp and file name
    log_file_name = f"differences.json"
    log_file_path = os.path.join(test_log_dir, log_file_name)

    # Write errors to JSON log file
    with open(log_file_path, 'w') as log_file:
        json.dump(errors, log_file, indent=4)

# Function to log messages to a log file
def log_message(message, test_log_dir):
    log_file_name = f"logs.txt"
    log_file_path = os.path.join(test_log_dir, log_file_name)

    with open(log_file_path, 'a') as log_file:
        log_file.write(message + '\n')

# Function to test atomic_search and compare result with expected counts
def test_atomic_search(file_name, log_dir, dataset_paths, min_atom_size, molecule_similarity, expected_mae, expected_r2, show_logs):
    js_folder, csv_file_path = dataset_paths

    y_true = [] 
    y_pred = [] 

    # Get list of all .js files or a specific file if provided
    if file_name:
        js_files = [file_name]
    else:
        js_files = [f for f in os.listdir(js_folder) if f.endswith('.js')]

    for js_file_name in js_files:
        js_file_path = os.path.join(js_folder, js_file_name)

        # Check if the JavaScript file exists
        if not os.path.exists(js_file_path):
            pytest.fail(f"JavaScript file '{js_file_name}' does not exist in the folder '{js_folder}'")

        # Read the JavaScript file content
        with open(js_file_path, 'r') as file:
            search_space = file.read()

        test_log_dir = get_log_dir(log_dir=log_dir, file_name=js_file_name)

        # Get the expected counts for the current JS file from the CSV
        expected_counts = read_expected_counts(csv_file_path, js_file_name)

        # Get the list of target words (keys of the expected counts)
        target_words = list(expected_counts.keys())

        f = io.StringIO()
        with contextlib.redirect_stdout(f): 
            # Run atomic_search to get the result for the current file
            results = atomic_search(
                target_words=target_words, 
                search_space=search_space, 
                min_atom_size=min_atom_size, 
                molecule_similarity=molecule_similarity, 
                logs=True
            )

        # Compare result with expected_counts
        errors = {}  # To store any mismatches between result and expected_counts

        for target_word in target_words:
            expected_count = expected_counts.get(target_word, 0)  # Get expected count for the target word
            result_count = results.get(target_word, 0)  # Get result count from atomic_search for the target word

            y_true.append(expected_count)  # Append expected count to y_true
            y_pred.append(result_count)    # Append result count to y_pred

            # If there is a mismatch, log the error
            if expected_count != result_count:
                errors[target_word] = {
                    'expected_count': expected_count,
                    'result_count': result_count
                }

        # Save logs if there are errors or if --show-logs is enabled
        if errors or show_logs:
            os.makedirs(test_log_dir, exist_ok=True)
            save_test_logs(test_log_dir, js_file_name, errors)
            log_output = f.getvalue()
            log_message(message=log_output, test_log_dir=test_log_dir)

    # Calculate evaluation metrics (MAE and R²)
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print(f"\nEvaluation Results for file {file_name or 'all files'}:")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Mean Squared Error (MSE): {mae:.2f}")
    print(f"R² Score: {r2:.2f}\n")

    # Assert to ensure the performance is as expected
    assert mae <= expected_mae, f"MAE should be less than {expected_mae} for good performance"
    assert r2 >= expected_r2, f"R² should be greater than {expected_r2} to indicate good accuracy"