import pytest
import os

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