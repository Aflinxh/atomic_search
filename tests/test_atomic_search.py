import os
import csv
import pytest
from atomic_search.atomic_search import atomic_search
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Function to read ground truth data from CSV
def read_ground_truth(csv_file_path):
    ground_truth = {}
    with open(csv_file_path, mode='r') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)  # Read the headers

        for row in reader:
            js_name = row[0]  # The first value is the js_name, which includes the full path
            values = {headers[i]: int(row[i]) for i in range(1, len(headers))}
            ground_truth[js_name] = values
    return ground_truth

# Test atomic_search on JavaScript files based on command line input
def test_atomic_search(dataset_paths, file_name, min_atom_size, molecule_similarity, expected_mae, expected_r2):
    js_folder, csv_file_path = dataset_paths

    # Read ground truth data
    ground_truth_data = read_ground_truth(csv_file_path)

    debugging=False

    if file_name:
        # Test a specific file if --file-name is provided
        js_file_name = file_name
        js_file_path = os.path.join(js_folder, js_file_name)

        # Check if the JavaScript file exists
        if not os.path.exists(js_file_path):
            pytest.fail(f"JavaScript file '{js_file_name}' does not exist in the folder '{js_folder}'")

        # Read the JavaScript file content
        with open(js_file_path, 'r') as file:
            js_code = file.read()

        # Use full path for matching in ground truth
        full_js_path = os.path.join(js_folder, js_file_name).replace("\\", "/")  # Ensure compatibility for different OS

        # If the file is not in the ground truth data, fail the test
        if full_js_path not in ground_truth_data:
            pytest.fail(f"Ground truth for file '{full_js_path}' does not exist in '{csv_file_path}'")

        gt_values = ground_truth_data[full_js_path]
        syntax_list = list(gt_values.keys())

        # Run atomic_search on the JavaScript code
        atomic_results = atomic_search(
            syntax_list,
            js_code,
            min_atom_size=min_atom_size,
            molecule_similarity=molecule_similarity,
            debugging=debugging
        )

        # Prepare y_true and y_pred for regression metrics for the current file
        y_true = [gt_values.get(syntax, 0) for syntax in syntax_list]
        y_pred = [atomic_results.get(syntax, 0) for syntax in syntax_list]

        # Calculate evaluation metrics for the current file
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # Print evaluation results for the current file
        print(f"\nEvaluation Results for file {js_file_name}:")
        print(f"Mean Absolute Error (MAE): {mae:.2f}")
        print(f"Mean Squared Error (MSE): {mse:.2f}")
        print(f"R² Score: {r2:.2f}\n")

        # Assert to verify the performance of the algorithm on the single file
        assert mae <= expected_mae, f"MAE for file '{js_file_name}' should be less than 0.1"
        assert r2 >= expected_r2, f"R² for file '{js_file_name}' should be greater than 0.9 to indicate a good accuracy"

    else:
        # If no specific file is provided, test all files in the folder
        syntax_list = list(next(iter(ground_truth_data.values())).keys())

        # List all JavaScript files in the folder
        js_files = [f for f in os.listdir(js_folder) if f.endswith('.js')]

        y_true = []
        y_pred = []

        # Iterate through each JavaScript file in the folder
        for js_file_name in js_files:
            js_file_path = os.path.join(js_folder, js_file_name)

            # Read JavaScript file content
            with open(js_file_path, 'r') as file:
                js_code = file.read()

            # Use full path for matching in ground truth
            full_js_path = os.path.join(js_folder, js_file_name).replace("\\", "/")

            # If the JavaScript file is not found in ground truth, skip it
            if full_js_path not in ground_truth_data:
                continue

            # Retrieve the ground truth values
            gt_values = ground_truth_data[full_js_path]
            
            # Run atomic_search on the JavaScript code
            atomic_results = atomic_search(
                syntax_list,
                js_code,
                min_atom_size=min_atom_size,
                molecule_similarity=molecule_similarity,
                debugging=debugging
            )

            # Prepare y_true and y_pred for regression metrics
            for syntax in syntax_list:
                y_true.append(gt_values.get(syntax, 0))
                y_pred.append(atomic_results.get(syntax, 0))

        # Calculate evaluation metrics for the whole folder
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # Print evaluation results for the whole folder
        print(f"\nEvaluation Results for all JavaScript files in the folder:")
        print(f"Mean Absolute Error (MAE): {mae:.2f}")
        print(f"Mean Squared Error (MSE): {mse:.2f}")
        print(f"R² Score: {r2:.2f}\n")

        # Assert to verify the overall performance
        assert mae <= expected_mae, "MAE should be less than 0.1 for good performance"
        assert r2 >= expected_r2, "R² should be greater than 0.9 to indicate a good accuracy"
