# conftest.py
def pytest_addoption(parser):
    parser.addoption(
        "--file-name", action="store", default=None, help="JavaScript file name to test (optional)"
    )