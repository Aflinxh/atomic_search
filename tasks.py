from invoke import task

@task
def clear_logs(c):
    """Clear log files"""
    c.run("python utils/clear_logs.py")

@task
def clear_datasets(c):
    """Clear datasets"""
    c.run("python utils/clear_datasets.py")

@task
def generate_datasets(c, num_samples=None):
    """Generate datasets, with optional number of samples"""
    num_samples_option = f"--num-samples={num_samples}" if num_samples else ""
    c.run(f"python utils/generate_datasets.py {num_samples_option}")

@task
def test_atoms(c, file_name=None, show_logs=False):
    """Run pytest for test_extract_atoms.py, with optional file-name and --show-logs"""
    show_logs_option = "--show-logs" if show_logs else ""
    file_name_option = f"--file-name={file_name}" if file_name else ""
    c.run(f"pytest tests/test_extract_atoms.py {file_name_option} {show_logs_option} -s")

@task
def test_molecule(c, file_name=None, show_logs=False):
    """Run pytest for test_form_molecule.py, with optional file-name and --show-logs"""
    show_logs_option = "--show-logs" if show_logs else ""
    file_name_option = f"--file-name={file_name}" if file_name else ""
    c.run(f"pytest tests/test_form_molecule.py {file_name_option} {show_logs_option} -s")

@task
def test_atomic(c, file_name=None, show_logs=False):
    """Run pytest for test_atomic_search.py, with optional file-name and --show-logs"""
    show_logs_option = "--show-logs" if show_logs else ""
    file_name_option = f"--file-name={file_name}" if file_name else ""
    c.run(f"pytest tests/test_atomic_search.py {file_name_option} {show_logs_option} -s")