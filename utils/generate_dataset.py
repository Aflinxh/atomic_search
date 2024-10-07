import random
import string
import csv
import os
import argparse

# Function to obfuscate syntax with concatenation (without additional noise)
def obfuscate_syntax(syntax):
    parts = [char for char in syntax]
    obfuscated_parts = []
    i = 0
    while i < len(parts):
        chunk_size = random.randint(1, 3)
        chunk = ''.join(parts[i:i + chunk_size])
        obfuscated_parts.append(f"'{chunk}'")
        i += chunk_size
    obfuscated_syntax = " + ".join(obfuscated_parts)
    return obfuscated_syntax

# Function to determine the number of syntax occurrences in each JavaScript file
def determine_syntax_counts(syntax_list, num_samples):
    syntax_counts_list = []
    for _ in range(num_samples):
        syntax_counts = {syntax: random.randint(0, 5) for syntax in syntax_list}
        syntax_counts_list.append(syntax_counts)
    return syntax_counts_list

# Function to generate JavaScript code based on the specified number of syntax occurrences
def generate_random_js(syntax_counts_list):
    js_samples = []
    for syntax_counts in syntax_counts_list:
        js_code = ""
        for syntax, count in syntax_counts.items():
            for _ in range(count):
                if random.random() > 0.5:
                    obfuscated = obfuscate_syntax(syntax)
                    js_code += obfuscated + "; "
                else:
                    js_code += syntax + "; "

                # Optionally add random comments to increase obfuscation (can be removed if not needed)
                if random.random() > 0.3:
                    random_comment = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 15)))
                    js_code += f"// {random_comment}\n"

                # Optionally add random JavaScript statements to add complexity (can be removed if not needed)
                if random.random() > 0.6:
                    random_var = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                    random_value = random.randint(1, 100)
                    js_code += f"var {random_var} = {random_value};\n"
        js_samples.append(js_code.strip())
    return js_samples

# Function to save obfuscated JavaScript files to the 'js' folder
def save_js_files(js_samples, folder_name="dataset-testing/js"):
    for idx, js_code in enumerate(js_samples):
        file_path = os.path.join(folder_name, f"sample_{idx + 1}.js")
        with open(file_path, mode='w') as file:
            file.write(js_code)

# Function to save data into a CSV file with 'js_name' column and feature columns for each syntax
def save_to_csv_with_features(syntax_counts_list, folder_name="dataset-testing", filename="obfuscated_js_dataset.csv"):
    file_path = os.path.join(folder_name, filename)
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ['js_name'] + list(syntax_counts_list[0].keys())
        writer.writerow(header)
        for idx, syntax_counts in enumerate(syntax_counts_list):
            js_name = os.path.join(folder_name, "js", f"sample_{idx + 1}.js")
            feature_counts = [syntax_counts[syntax] for syntax in syntax_counts]
            writer.writerow([js_name] + feature_counts)

# Main function
def main():
    parser = argparse.ArgumentParser(description="Generate obfuscated JavaScript dataset.")
    parser.add_argument('--num_samples', type=int, default=10, help='Number of JavaScript samples to generate')
    args = parser.parse_args()

    syntax_list = [
        'getElementById', 'querySelector', 'addEventListener',
        'setTimeout', 'localStorage', 'sessionStorage',
        'innerHTML', 'console', 'log', 'eval',
    ]

    # Create 'dataset-testing' and 'js' folders if they do not exist
    dataset_folder = "dataset-testing"
    js_folder = os.path.join(dataset_folder, "js")

    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    if not os.path.exists(js_folder):
        os.makedirs(js_folder)

    # Determine the number of syntax occurrences for each generated JavaScript file
    num_samples = args.num_samples  # Number of samples to generate from command line argument (default is 10)
    syntax_counts_list = determine_syntax_counts(syntax_list, num_samples)

    # Generate dataset with obfuscated JavaScript
    js_samples = generate_random_js(syntax_counts_list)

    # Save obfuscated JavaScript files to 'dataset-testing/js'
    save_js_files(js_samples, js_folder)

    # Save dataset with features to 'dataset-testing'
    save_to_csv_with_features(syntax_counts_list, dataset_folder)

    print(f"JavaScript dataset has been saved in the folder '{js_folder}', and the CSV file has been saved in the folder '{dataset_folder}'.")

if __name__ == "__main__":
    main()