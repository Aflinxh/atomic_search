import random
import string
import csv
import os
import argparse
import json
from pprint import pprint

# Function to create atoms for each target word based on syntax count requirements
def create_atoms(target_words, syntax_counts_list, min_atom_size=1, max_atom_size=3):
    atoms_list = []

    # Iterate over each sample's syntax counts
    for syntax_counts in syntax_counts_list:
        atoms = {}
        atom_id = 1
        # Add a section for ambiguous words
        atoms['ambiguous_word'] = []

        for target in target_words:
            if not target:  # Skip if the target word is empty
                continue

            atoms[target] = []
            count = syntax_counts.get(target, 0)  # Get the count of the current target in this sample

            for _ in range(count):
                # Randomly decide whether to use the full target_word as a single atom or split it
                if random.random() > 0.5:
                    # Use the full target word as a single atom
                    atoms[target].append({
                        'id': atom_id,
                        'value': target,
                        'used': False,
                        'ref': target
                    })
                    atom_id += 1
                else:
                    # Split the target word into smaller atoms with random sizes
                    i = 0
                    while i < len(target):
                        # Generate a random size for the atom between min_atom_size and max_atom_size
                        atom_size = random.randint(min_atom_size, max_atom_size)
                        value = target[i:i + atom_size]
                        if value:  # Ensure it's not an empty string
                            # Check if the split atom matches with any other target word
                            is_ambiguous = False
                            for other_target in target_words:
                                if other_target != target and value in other_target:
                                    is_ambiguous = True
                                    break

                            if is_ambiguous:
                                # Add to ambiguous words
                                atoms['ambiguous_word'].append({
                                    'id': atom_id,
                                    'value': value,
                                    'used': False,
                                    'ref': 'ambiguous_word'
                                })
                            else:
                                # Add to the original target word atoms list
                                atoms[target].append({
                                    'id': atom_id,
                                    'value': value,
                                    'used': False,
                                    'ref': target
                                })

                            atom_id += 1
                        i += atom_size

        atoms_list.append(atoms)

    return atoms_list

# Function to determine the number of syntax occurrences in each JavaScript file
def determine_syntax_counts(syntax_list, num_samples):
    syntax_counts_list = []
    for _ in range(num_samples):
        syntax_counts = {syntax: random.randint(0, 5) for syntax in syntax_list}
        syntax_counts_list.append(syntax_counts)
    return syntax_counts_list

# Function to generate valid noise that does not match any part of target words
def generate_valid_noise(target_words, noise_length):
    while True:
        noise = ''.join(random.choices(string.ascii_letters + string.digits, k=noise_length))
        if not any(noise in target for target in target_words):
            return noise

# Function to generate JavaScript code using all atoms from atoms_list without leaving any unused
def generate_random_js(atoms_list, target_words):
    js_samples = []

    # Iterate over each atom set for each sample
    for sample_index, atoms in enumerate(atoms_list):
        all_atoms = []

        # Flatten all atoms from all target words into one list
        for atom_list in atoms.values():
            all_atoms.extend(atom_list)

        # Shuffle the atom list to create randomness
        random.shuffle(all_atoms)

        js_code = ""

        # Iterate through all shuffled atoms to build the JavaScript code
        while any(not atom['used'] for atom in all_atoms):
            atom = random.choice(all_atoms)

            if not atom['used']:
                # Decide randomly how to use the atom
                if random.random() > 0.5:
                    # Wrap atom value in single quotes and add concatenation symbol '+'
                    js_code += f"'{atom['value']}' + "
                else:
                    # Use the atom as a whole command followed by a semicolon
                    js_code += f"{atom['value']}; "

                # Mark the atom as used
                atom['used'] = True

                # Randomly decide to add a variable declaration with random value
                if random.random() > 0.6:
                    var_name = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                    var_value = random.randint(1, 100)
                    js_code += f"var {var_name} = {var_value};\n"

                # Randomly decide to add a comment for obfuscation
                if random.random() > 0.4:
                    noise_length = random.randint(5, 15)
                    random_comment = generate_valid_noise(target_words, noise_length)
                    js_code += f"// {random_comment}\n"

        # Clean up the ending '+' if it exists
        if js_code.endswith(' + '):
            js_code = js_code[:-3] + ";\n"

        js_samples.append(js_code.strip())

    return js_samples

# Function to save obfuscated JavaScript files to the 'js' folder
def save_js_files(js_samples, folder_name="dataset-testing/js"):
    # Ensure the directory exists
    os.makedirs(folder_name, exist_ok=True)
    
    for idx, js_code in enumerate(js_samples):
        file_path = os.path.join(folder_name, f"sample_{idx + 1}.js")
        with open(file_path, mode='w') as file:
            file.write(js_code)

# Function to save data into a CSV file with 'js_name' column and feature columns for each syntax and atoms
def save_to_csv_with_features(syntax_counts_list, atoms_list, folder_name="dataset-testing", filename="obfuscated_js_dataset.csv"):
    file_path = os.path.join(folder_name, filename)
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Header: js_name, syntax features, and atoms
        header = ['js_name'] + list(syntax_counts_list[0].keys()) + ['atoms']
        writer.writerow(header)

        for idx, (syntax_counts, atoms) in enumerate(zip(syntax_counts_list, atoms_list)):
            js_name = os.path.join(folder_name, "js", f"sample_{idx + 1}.js")
            feature_counts = [syntax_counts[syntax] for syntax in syntax_counts]

            # Save atoms as JSON formatted string for better readability in CSV
            atoms_str = json.dumps(atoms)

            writer.writerow([js_name] + feature_counts + [atoms_str])

# Main function
def main():
    parser = argparse.ArgumentParser(description="Generate obfuscated JavaScript dataset.")
    parser.add_argument('--num-samples', type=int, default=10, help='Number of JavaScript samples to generate')
    args = parser.parse_args()

    syntax_list = [
        'getElementById', 'querySelector', 'addEventListener',
        'setTimeout', 'localStorage', 'sessionStorage',
        'innerHTML', 'console', 'log', 'eval',
    ]

    # Determine the number of syntax occurrences for each generated JavaScript file
    num_samples = args.num_samples  # Number of samples to generate from command line argument (default is 10)
    syntax_counts_list = determine_syntax_counts(syntax_list, num_samples)

    # Create atoms for each target word with random length between min_atom_size and max_atom_size or use the whole target as a single atom
    atoms_list = create_atoms(syntax_list, syntax_counts_list, min_atom_size=1, max_atom_size=3)

    # Save dataset with features to 'dataset-testing', including atoms
    save_to_csv_with_features(syntax_counts_list, atoms_list, folder_name="dataset-testing")

    # Generate dataset with obfuscated JavaScript using defined atoms in random order
    js_samples = generate_random_js(atoms_list, syntax_list)

    # Save obfuscated JavaScript files to 'dataset-testing/js'
    save_js_files(js_samples, "dataset-testing/js")

    print(f"JavaScript dataset has been saved in the folder 'dataset-testing/js', and the CSV file has been saved in the folder 'dataset-testing'.")

if __name__ == "__main__":
    main()
