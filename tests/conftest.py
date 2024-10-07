import pytest
import os
import json
import datetime as dt
import pytz


@pytest.fixture
def min_atom_size():
    return "1"

@pytest.fixture
def molecule_similarity():
    return "100%"

@pytest.fixture
def expected_mae():
    return 0.3

@pytest.fixture
def expected_r2():
    return 0.9    

@pytest.fixture
def file_name(request):
    return request.config.getoption("--file-name")


# conftest.py
def pytest_addoption(parser):
    parser.addoption("--file-name", action="store", default=None, help="JavaScript file name to test (optional)")
    parser.addoption("--log-dir", action="store", default="logs", help="Directory to store logs (default is 'logs')")

# Fixture to prepare dataset paths and expected atoms from CSV
@pytest.fixture
def dataset_paths():
    js_folder = 'dataset-testing/js'
    csv_file_path = 'dataset-testing/obfuscated_js_dataset.csv'
    return js_folder, csv_file_path

@pytest.fixture
def log_dir(request):
    # Get the value of log directory from command line options, with 'logs' as default
    log_dir = request.config.getoption("--log-dir")
    
    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    return log_dir

# Update the save_test_logs function to handle differences
def save_test_logs(test_name, log_dir, filtered_result, filtered_expected, differences):
    jakarta_tz = pytz.timezone('Asia/Jakarta')

    # Create the folder structure for logs
    time_stamp = dt.datetime.now(jakarta_tz).strftime("%Y-%m-%d_%H-%M-%S")
    test_log_dir = os.path.join(log_dir, f"{test_name}/{time_stamp}")
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