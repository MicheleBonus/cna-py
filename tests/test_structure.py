import pytest
from pathlib import Path
import numpy as np
import biotite.structure as struc

from cna.io import readers
from cna.structure.system import MolecularSystem

# Define the path to the test data directory relative to this test file
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PDB_FILE = TEST_DATA_DIR / "test.pdb"

# Use the same expected atom count as in test_io.py
EXPECTED_ATOMS = 75

@pytest.fixture(scope="module")
def loaded_atom_array() -> struc.AtomArray:
    """
    Pytest fixture to load the test PDB file once for all tests in this module.
    """
    try:
        return readers.load_structure(TEST_PDB_FILE)
    except Exception as e:
        pytest.fail(f"Fixture failed to load test PDB {TEST_PDB_FILE}: {e}")

def test_molecular_system_init(loaded_atom_array: struc.AtomArray):
    """
    Tests the initialization of the MolecularSystem class.
    """
    assert isinstance(loaded_atom_array, struc.AtomArray), "Fixture did not return AtomArray"

    system = MolecularSystem(loaded_atom_array)

    assert isinstance(system, MolecularSystem), "Failed to initialize MolecularSystem"
    # Check if the exact same object is stored (identity check)
    assert system._atom_array is loaded_atom_array, "Internal AtomArray is not the same object"
    assert len(system) == EXPECTED_ATOMS, "Length via __len__ is incorrect"
    assert repr(system) == f"<MolecularSystem ({EXPECTED_ATOMS} atoms)>", "Repr is incorrect"


def test_molecular_system_properties(loaded_atom_array: struc.AtomArray):
    """
    Tests the basic properties of the MolecularSystem class.
    """
    system = MolecularSystem(loaded_atom_array)

    # Test atom_count property
    assert system.atom_count == EXPECTED_ATOMS, \
        f"Expected atom_count {EXPECTED_ATOMS}, got {system.atom_count}"
    assert system.atom_count == len(loaded_atom_array), \
        "atom_count does not match length of underlying AtomArray"

    # Test coords property
    assert isinstance(system.coords, np.ndarray), "coords property should return a NumPy array"
    assert system.coords.shape == (EXPECTED_ATOMS, 3), \
        f"Expected coords shape ({EXPECTED_ATOMS}, 3), got {system.coords.shape}"
    assert system.coords.dtype == np.float32, \
        "Expected coords dtype float32" # Biotite uses float32
    np.testing.assert_array_equal(system.coords, loaded_atom_array.coord,
                                   err_msg="coords property does not match underlying AtomArray coordinates")

    # Test atom_array property
    assert system.atom_array is loaded_atom_array, \
        "atom_array property does not return the correct underlying AtomArray object"

def test_molecular_system_init_wrong_type():
    """
    Tests that MolecularSystem raises TypeError if not initialized with AtomArray.
    """
    with pytest.raises(TypeError):
        MolecularSystem("not an atom array") # type: ignore

    with pytest.raises(TypeError):
        # Create a dummy AtomArrayStack
        atom1 = struc.Atom([1.0, 2.0, 3.0], atom_name="CA", res_name="ALA", res_id=1)
        atom_array1 = struc.array([atom1])
        atom_array2 = struc.array([atom1]) # Duplicate for stack
        stack = struc.stack([atom_array1, atom_array2])
        MolecularSystem(stack) # type: ignore
