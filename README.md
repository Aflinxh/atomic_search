# Atomic Search

**Atomic Search** is a Python package for detecting malicious JavaScript syntax through an atomic and molecule search approach. This package is designed to handle obfuscated JavaScript code using techniques like concatenation and syntax splitting, making it effective for detecting target syntax even when the code is heavily obfuscated.

## Features

- **Atomic Extraction**: Extracts relevant syntax fragments (atoms) from obfuscated JavaScript.
- **Molecule Search**: Combines these atoms to form specific target syntax using a brute-force approach, enabling the detection of malicious JavaScript syntax.
- **Logging and Debugging**: Logs the extraction and molecule formation process for debugging purposes.
- **Automated Task Management**: Simplify development tasks with `invoke` commands.

## Installation

Ensure you are using Python 3.7 or newer.

1. Clone the repository:
   ```bash
   git clone https://github.com/aflinxh/atomic_search.git
   cd atomic_search
   ```

2. Install the package using `pip`:
   ```bash
   pip install .
   ```

3. For development, install additional dependencies:
   ```bash
   pip install .[dev]
   ```

## Usage

Here’s an example of using **Atomic Search** to detect JavaScript syntax:

```python
from atomic_search import atomic_search

# List of target words to detect
target_words = ["getElementById", "addEventListener"]

# Example search space, which is obfuscated JavaScript code
search_space = "some obfuscated JavaScript code"

# Define minimum atom size and molecule similarity
min_atom_size = 2  # minimum atom size
molecule_similarity = {"getElementById": "90%", "addEventListener": "-2"}  # tolerance or similarity level

# Run the atomic search
results = atomic_search(target_words, search_space, min_atom_size, molecule_similarity, logs=True)

# Display the results
print("Search Results:", results)
```

### `atomic_search` Function Parameters

- **`target_words`**: List of strings representing the target syntax to detect.
- **`search_space`**: The JavaScript string to analyze.
- **`min_atom_size`**: Minimum atom size required for validity.
- **`molecule_similarity`**: Dictionary setting the similarity or tolerance for each target.
- **`logs`**: Set to `True` to display logs.

## Directory Structure

The project has the following structure:

```
atomic_search/
├── atomic_search.py        # Main function for atom and molecule search
├── extract_atoms.py        # Module for atom extraction
├── form_molecule.py        # Module to form molecules from atoms
└── __init__.py             # Package initializer
tasks.py                    # Task automation with Invoke
utils/                      # Utility scripts for managing logs and datasets
tests/                      # Test directory
README.md                   # This documentation
pyproject.toml              # Project metadata
setup.py                    # Installation configuration
```

## Utility Commands

This project uses `invoke` to manage development tasks, which are defined in `tasks.py`. Here are some commonly used commands:

- **Clear Logs**: Removes all log files from the logs directory.
  ```bash
  invoke clear-logs
  ```

- **Clear Datasets**: Removes all datasets from the dataset directory.
  ```bash
  invoke clear-datasets
  ```

- **Generate Datasets**: Generates datasets with an optional `num_samples` argument.
  ```bash
  invoke generate-datasets --num-samples=100
  ```

## Testing

This project uses `pytest` for running tests and `invoke` to manage and simplify test execution. Here are the available test commands using `invoke`:

- **Run Atom Tests**: Runs tests for `extract_atoms.py` located in `tests/test_extract_atoms.py`. You can optionally specify a particular file to test and enable logs.

  ```bash
  invoke test-atoms --file-name="sample.js" --show-logs
  ```
  - `--file-name`: Specifies the JavaScript file to use for testing.
  - `--show-logs`: Enables detailed logging during the test.

- **Run Molecule Tests**: Runs tests for `form_molecule.py` located in `tests/test_form_molecule.py`. You can optionally specify a file name and enable logs.

  ```bash
  invoke test-molecule --file-name="sample.js" --show-logs
  ```
  - `--file-name`: Specifies the JavaScript file to use for testing.
  - `--show-logs`: Enables detailed logging during the test.

- **Run Atomic Search Tests**: Runs tests for the `atomic_search` function located in `tests/test_atomic_search.py`. You can specify a file name and enable logs, similar to the other test commands.

  ```bash
  invoke test-atomic --file-name="sample.js" --show-logs
  ```
  - `--file-name`: Specifies the JavaScript file to use for testing.
  - `--show-logs`: Enables detailed logging during the test.

### Running All Tests

To run all tests in the `tests/` directory, you can use `pytest` directly:

```bash
pytest tests/
```

These `invoke` commands allow you to run targeted tests with specific options for more control during development and debugging.


## Contribution

Contributions are welcome! Follow these steps to contribute:

1. Fork this repository.
2. Create a branch for your feature or fix (`git checkout -b new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin new-feature`).
5. Create a Pull Request.

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.