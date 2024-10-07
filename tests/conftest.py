import pytest

# conftest.py
def pytest_addoption(parser):
    parser.addoption(
        "--file-name", action="store", default=None, help="JavaScript file name to test (optional)"
    )

@pytest.fixture
def min_atom_size():
    return "1"

@pytest.fixture
def molecule_similarity():
    return "100%"

@pytest.fixture
def common_atoms():
    return {
        'mencarik': [
            {'id': 1, 'value': 'men', 'used': False, 'ref': 'mencarik'},
            {'id': 2, 'value': 'rik', 'used': False, 'ref': 'mencarik'},
            {'id': 3, 'value': 'ca', 'used': False, 'ref': 'mencarik'},
            {'id': 4, 'value': 'nc', 'used': False, 'ref': 'mencarik'},
            {'id': 6, 'value': 'm', 'used': False, 'ref': 'mencarik'},
            {'id': 8, 'value': 'ar', 'used': False, 'ref': 'mencarik'},
            {'id': 9, 'value': 'nc', 'used': False, 'ref': 'mencarik'},
            {'id': 10, 'value': 'i', 'used': False, 'ref': 'mencarik'},
            {'id': 11, 'value': 'k', 'used': False, 'ref': 'mencarik'}
        ],
        'ambiguous_word': [
            {'id': 5, 'value': 'a', 'used': False, 'ref': 'ambiguous_word'},
            {'id': 7, 'value': 'e', 'used': False, 'ref': 'ambiguous_word'},
            {'id': 12, 'value': 'a', 'used': False, 'ref': 'ambiguous_word'},
            {'id': 17, 'value': 'a', 'used': False, 'ref': 'ambiguous_word'}
        ],
        'test': [
            {'id': 13, 'value': 'st', 'used': False, 'ref': 'test'},
            {'id': 15, 'value': 'te', 'used': False, 'ref': 'test'}
        ],
        'apa': [
            {'id': 14, 'value': 'pa', 'used': False, 'ref': 'apa'},
            {'id': 16, 'value': 'pa', 'used': False, 'ref': 'apa'},
            {'id': 18, 'value': 'pa', 'used': False, 'ref': 'apa'}
        ]
    }