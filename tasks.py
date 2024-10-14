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
    if num_samples:
        c.run(f"python utils/generate_datasets.py --num-samples={num_samples}")
    else:
        c.run("python utils/generate_datasets.py")

@task
def test_atoms(c, file_name=None):
    """Run pytest for test_extract_atoms.py, with optional file-name"""
    if file_name:
        c.run(f"pytest tests/test_extract_atoms.py --file-name={file_name} -s")
    else:
        c.run("pytest tests/test_extract_atoms.py -s")

@task
def test_molecule(c, file_name=None):
    """Run pytest for test_form_molecule.py, with optional file-name"""
    if file_name:
        c.run(f"pytest tests/test_form_molecule.py --file-name={file_name} -s")
    else:
        c.run("pytest tests/test_form_molecule.py -s")

@task
def test_atomic(c, file_name=None):
    """Run pytest for test_atomic_search.py, with optional file-name"""
    if file_name:
        c.run(f"pytest tests/test_atomic_search.py --file-name={file_name} -s")
    else:
        c.run("pytest tests/test_atomic_search.py -s")