import pytest
from pathlib import Path
import biotite.structure as struc
from cna.io import readers

# Define the path to the test data directory relative to this test file
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PDB_FILE = TEST_DATA_DIR / "test.pdb"

# Define an expected number of atoms for the test file
# NOTE: Adjust this value based on the actual content of tests/data/test.pdb
EXPECTED_ATOMS = 75 # Assuming a small protein snippet for testing

# Ensure the test PDB file exists (useful for CI or new setups)
@pytest.fixture(scope="module", autouse=True)
def check_test_pdb_exists():
    if not TEST_PDB_FILE.is_file():
        pytest.fail(
            f"Test PDB file not found at {TEST_PDB_FILE}. "
            "Please create a small valid PDB file for testing."
        )

def test_load_pdb_structure_success():
    """
    Tests successful loading of a PDB file using load_structure.
    """
    try:
        atom_array = readers.load_structure(TEST_PDB_FILE)
    except FileNotFoundError:
        pytest.fail(f"Test PDB file failed to load: {TEST_PDB_FILE} not found.")
    except ValueError as e:
        pytest.fail(f"Test PDB file failed to parse: {e}")
    except Exception as e:
         pytest.fail(f"An unexpected error occurred during loading: {e}")


    assert isinstance(atom_array, struc.AtomArray), \
        "load_structure should return a biotite.AtomArray"
    assert len(atom_array) == EXPECTED_ATOMS, \
        f"Expected {EXPECTED_ATOMS} atoms, but found {len(atom_array)}"

def test_load_structure_file_not_found():
    """
    Tests that load_structure raises FileNotFoundError for non-existent files.
    """
    non_existent_file = TEST_DATA_DIR / "non_existent.pdb"
    assert not non_existent_file.exists(), "Test assumes file does not exist"

    with pytest.raises(FileNotFoundError):
        readers.load_structure(non_existent_file)

# Optional: Test for handling multiple models if a suitable test file is available
# def test_load_structure_multiple_models():
#     multi_model_file = TEST_DATA_DIR / "multi_model.pdb" # Assumes this file exists
#     if not multi_model_file.is_file():
#          pytest.skip(f"Multi-model test file not found at {multi_model_file}")
#
#     with pytest.warns(UserWarning, match="multiple models"): # Check for warning
#         atom_array = readers.load_structure(multi_model_file)
#
#     assert isinstance(atom_array, struc.AtomArray)
#     # Add assertion for expected atom count of the *first* model
