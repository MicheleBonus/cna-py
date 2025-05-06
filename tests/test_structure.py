# File: tests/test_structure.py
# Content:

import pytest
from pathlib import Path
import numpy as np
import biotite.structure as struc

from cna.io import readers
from cna.structure.system import MolecularSystem

# Define the path to the test data directory relative to this test file
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PDB_FILE = TEST_DATA_DIR / "01_simple_helix.pdb"
TEST_CIF_FILE = TEST_DATA_DIR / "01_simple_helix.cif"

# Use the correct expected atom count
EXPECTED_ATOMS = 336

@pytest.fixture(scope="module")
def loaded_atom_array_pdb() -> struc.AtomArray:
    """
    Pytest fixture to load the test PDB file once for all tests in this module.
    """
    try:
        return readers.load_structure(TEST_PDB_FILE)
    except Exception as e:
        pytest.fail(f"Fixture failed to load test PDB {TEST_PDB_FILE}: {e}")

@pytest.fixture(scope="module")
def loaded_atom_array_cif() -> struc.AtomArray:
    """
    Pytest fixture to load the test CIF file once for all tests in this module.
    """
    try:
        return readers.load_structure(TEST_CIF_FILE)
    except Exception as e:
        pytest.fail(f"Fixture failed to load test CIF {TEST_CIF_FILE}: {e}")


# --- Tests using PDB input ---

def test_molecular_system_init_pdb(loaded_atom_array_pdb: struc.AtomArray):
    """
    Tests the initialization of the MolecularSystem class using PDB data.
    """
    assert isinstance(loaded_atom_array_pdb, struc.AtomArray), "PDB Fixture did not return AtomArray"

    system = MolecularSystem(loaded_atom_array_pdb)

    assert isinstance(system, MolecularSystem), "Failed to initialize MolecularSystem from PDB"
    assert system._atom_array is loaded_atom_array_pdb, "Internal AtomArray (PDB) is not the same object"
    assert len(system) == EXPECTED_ATOMS, "Length via __len__ (PDB) is incorrect"
    assert repr(system) == f"<MolecularSystem ({EXPECTED_ATOMS} atoms)>", "Repr (PDB) is incorrect"


def test_molecular_system_properties_pdb(loaded_atom_array_pdb: struc.AtomArray):
    """
    Tests the basic properties of the MolecularSystem class using PDB data.
    """
    system = MolecularSystem(loaded_atom_array_pdb)

    # Test atom_count property
    assert system.atom_count == EXPECTED_ATOMS, \
        f"PDB: Expected atom_count {EXPECTED_ATOMS}, got {system.atom_count}"
    assert system.atom_count == len(loaded_atom_array_pdb), \
        "PDB: atom_count does not match length of underlying AtomArray"

    # Test coords property
    assert isinstance(system.coords, np.ndarray), "PDB: coords property should return a NumPy array"
    assert system.coords.shape == (EXPECTED_ATOMS, 3), \
        f"PDB: Expected coords shape ({EXPECTED_ATOMS}, 3), got {system.coords.shape}"
    assert system.coords.dtype == np.float32, \
        "PDB: Expected coords dtype float32"
    np.testing.assert_array_equal(system.coords, loaded_atom_array_pdb.coord,
                                   err_msg="PDB: coords property does not match underlying AtomArray coordinates")

    # Test atom_array property
    assert system.atom_array is loaded_atom_array_pdb, \
        "PDB: atom_array property does not return the correct underlying AtomArray object"

# --- Tests using CIF input ---

def test_molecular_system_init_cif(loaded_atom_array_cif: struc.AtomArray):
    """
    Tests the initialization of the MolecularSystem class using CIF data.
    """
    assert isinstance(loaded_atom_array_cif, struc.AtomArray), "CIF Fixture did not return AtomArray"

    system = MolecularSystem(loaded_atom_array_cif)

    assert isinstance(system, MolecularSystem), "Failed to initialize MolecularSystem from CIF"
    assert system._atom_array is loaded_atom_array_cif, "Internal AtomArray (CIF) is not the same object"
    assert len(system) == EXPECTED_ATOMS, "Length via __len__ (CIF) is incorrect"
    assert repr(system) == f"<MolecularSystem ({EXPECTED_ATOMS} atoms)>", "Repr (CIF) is incorrect"

def test_molecular_system_properties_cif(loaded_atom_array_cif: struc.AtomArray):
    """
    Tests the basic properties of the MolecularSystem class using CIF data.
    """
    system = MolecularSystem(loaded_atom_array_cif)

    # Test atom_count property
    assert system.atom_count == EXPECTED_ATOMS, \
        f"CIF: Expected atom_count {EXPECTED_ATOMS}, got {system.atom_count}"
    assert system.atom_count == len(loaded_atom_array_cif), \
        "CIF: atom_count does not match length of underlying AtomArray"

    # Test coords property
    assert isinstance(system.coords, np.ndarray), "CIF: coords property should return a NumPy array"
    assert system.coords.shape == (EXPECTED_ATOMS, 3), \
        f"CIF: Expected coords shape ({EXPECTED_ATOMS}, 3), got {system.coords.shape}"
    assert system.coords.dtype == np.float32, \
        "CIF: Expected coords dtype float32"
    # Compare coordinates between PDB and CIF loaded structures (should be almost identical)
    pdb_coords = loaded_atom_array_cif.coord # Reuse CIF fixture for coords
    np.testing.assert_allclose(system.coords, pdb_coords, atol=1e-3,
                                err_msg="CIF: coords property does not match CIF AtomArray coordinates") # Use allclose due to potential float representation differences

    # Test atom_array property
    assert system.atom_array is loaded_atom_array_cif, \
        "CIF: atom_array property does not return the correct underlying AtomArray object"


# --- Error Handling Test ---

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

# --- Future Test Cases (Placeholders) ---
# These would involve creating MolecularSystem instances from the future test files
# loaded in test_io.py and verifying specific properties (e.g., atom counts,
# presence of specific residue names or elements, etc.)

# @pytest.mark.skip(reason="Depends on future test files and potentially new MolecularSystem methods")
# def test_molecular_system_with_ligand():
#     """Tests MolecularSystem initialized with a structure containing a ligand."""
#     # Needs fixture loading protein_with_ligand.pdb
#     # system = MolecularSystem(loaded_ligand_structure_fixture)
#     # assert "LIG" in system.atom_array.res_name # Or use a potential system.get_residue_names() method
#     pass

# @pytest.mark.skip(reason="Depends on future test files and potentially new MolecularSystem methods")
# def test_molecular_system_with_disulfides():
#     """Tests MolecularSystem initialized with a structure containing disulfides."""
#     # Needs fixture loading protein_with_ssbond.pdb
#     # system = MolecularSystem(loaded_ssbond_structure_fixture)
#     # Add specific checks, perhaps using system.detect_disulfides() if implemented later
#     pass