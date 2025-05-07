# File: tests/test_io.py
# Content:

import pytest
from pathlib import Path
import biotite.structure as struc
from biotite.structure.error import BadStructureError
from cna.io import readers
import logging

# Setup logger for testing specific messages if needed
logger = logging.getLogger(__name__)

# Define the path to the test data directory relative to this test file
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PDB_FILE = TEST_DATA_DIR / "01_simple_helix.pdb"
TEST_CIF_FILE = TEST_DATA_DIR / "01_simple_helix.cif"

# Define the expected number of atoms for the test files
EXPECTED_ATOMS = 336

# Ensure the test files exist (useful for CI or new setups)
@pytest.fixture(scope="module", autouse=True)
def check_test_files_exist():
    """Fixture to ensure necessary test structure files exist."""
    files_to_check = [TEST_PDB_FILE, TEST_CIF_FILE]
    missing_files = [f for f in files_to_check if not f.is_file()]
    if missing_files:
        pytest.fail(
            f"Test structure file(s) not found: {', '.join(map(str, missing_files))}. "
            "Please ensure these files exist in the tests/data directory."
        )

def test_load_pdb_structure_success():
    """
    Tests successful loading of a standard PDB file (with H and caps) using load_structure.
    """
    try:
        atom_array = readers.load_structure(TEST_PDB_FILE)
    except FileNotFoundError:
        pytest.fail(f"Test PDB file failed to load: {TEST_PDB_FILE} not found.")
    except (ValueError, BadStructureError) as e:
        pytest.fail(f"Test PDB file failed to parse: {e}")
    except Exception as e:
         pytest.fail(f"An unexpected error occurred during PDB loading: {e}")

    assert isinstance(atom_array, struc.AtomArray), \
        "load_structure from PDB should return a biotite.AtomArray"
    assert len(atom_array) == EXPECTED_ATOMS, \
        f"PDB: Expected {EXPECTED_ATOMS} atoms, but found {len(atom_array)}"
    # Add checks for presence of hydrogens and caps if needed (e.g., check element list)
    assert "H" in atom_array.element, "Expected Hydrogens to be present in the loaded PDB"
    assert "ACE" in atom_array.res_name, "Expected ACE cap to be present"
    assert "NMA" in atom_array.res_name, "Expected NMA cap to be present"


def test_load_cif_structure_success():
    """
    Tests successful loading of a standard mmCIF file (with H and caps) using load_structure.
    """
    try:
        atom_array = readers.load_structure(TEST_CIF_FILE)
    except FileNotFoundError:
        pytest.fail(f"Test CIF file failed to load: {TEST_CIF_FILE} not found.")
    except (ValueError, BadStructureError) as e:
        pytest.fail(f"Test CIF file failed to parse: {e}")
    except Exception as e:
         pytest.fail(f"An unexpected error occurred during CIF loading: {e}")

    assert isinstance(atom_array, struc.AtomArray), \
        "load_structure from CIF should return a biotite.AtomArray"
    assert len(atom_array) == EXPECTED_ATOMS, \
        f"CIF: Expected {EXPECTED_ATOMS} atoms, but found {len(atom_array)}"
     # Add checks for presence of hydrogens and caps if needed
    assert "H" in atom_array.element, "Expected Hydrogens to be present in the loaded CIF"
    assert "ACE" in atom_array.res_name, "Expected ACE cap to be present in loaded CIF"
    assert "NMA" in atom_array.res_name, "Expected NMA cap to be present in loaded CIF"

def test_load_structure_file_not_found():
    """
    Tests that load_structure raises FileNotFoundError for non-existent files.
    """
    non_existent_file = TEST_DATA_DIR / "non_existent_structure.pdb"
    assert not non_existent_file.exists(), "Test assumes file does not exist"

    with pytest.raises(FileNotFoundError):
        readers.load_structure(non_existent_file)

# --- Future Test Cases (Placeholders) ---
# To implement these, create corresponding files in tests/data/

# @pytest.mark.skip(reason="Test file not yet created")
# def test_load_pdb_no_hydrogens():
#     """Tests loading a PDB file without explicit hydrogen atoms."""
#     # test_file = TEST_DATA_DIR / "protein_no_h.pdb"
#     # atom_array = readers.load_structure(test_file)
#     # assert "H" not in atom_array.element
#     # assert len(atom_array) == EXPECTED_ATOMS_NO_H # Define this
#     pass

# @pytest.mark.skip(reason="Test file not yet created")
# def test_load_pdb_with_ligand():
#     """Tests loading a PDB file containing a common ligand (HETATM)."""
#     # test_file = TEST_DATA_DIR / "protein_with_ligand.pdb"
#     # atom_array = readers.load_structure(test_file)
#     # assert any(atom_array.hetero) # Check if any atom is marked as HETATM
#     # ligands = atom_array[atom_array.hetero]
#     # assert "LIG" in ligands.res_name # Replace LIG with actual ligand name
#     # assert len(atom_array) == EXPECTED_ATOMS_WITH_LIGAND # Define this
#     pass

# @pytest.mark.skip(reason="Test file not yet created")
# def test_load_pdb_with_cofactor():
#     """Tests loading a PDB file containing a common cofactor (e.g., Heme, NAD)."""
#     # test_file = TEST_DATA_DIR / "protein_with_cofactor.pdb"
#     # atom_array = readers.load_structure(test_file)
#     # assert any(atom_array.hetero)
#     # cofactors = atom_array[atom_array.hetero]
#     # assert "HEM" in cofactors.res_name # Replace HEM with actual cofactor name
#     # assert len(atom_array) == EXPECTED_ATOMS_WITH_COFACTOR # Define this
#     pass

# @pytest.mark.skip(reason="Test file not yet created")
# def test_load_pdb_with_disulfides():
#     """Tests loading a PDB file with known disulfide bridges."""
#     # Needs a way to verify disulfide detection post-loading, likely in structure module.
#     # test_file = TEST_DATA_DIR / "protein_with_ssbond.pdb"
#     # atom_array = readers.load_structure(test_file)
#     # assert len(atom_array) == EXPECTED_ATOMS_WITH_SSBOND # Define this
#     # Add check for CYS SG-SG distances or Biotite's disulfide detection if used later.
#     pass

# @pytest.mark.skip(reason="Test file not yet created")
# def test_load_pdb_covalent_ligand():
#     """Tests loading a PDB with a covalently bound HETATM."""
#     # Verification might need connectivity info post-loading.
#     # test_file = TEST_DATA_DIR / "protein_covalent_ligand.pdb"
#     # atom_array = readers.load_structure(test_file)
#     # assert len(atom_array) == EXPECTED_ATOMS_WITH_COVALENT_LIGAND # Define this
#     pass

# @pytest.mark.skip(reason="Test file not yet created")
# def test_load_pdb_multiple_models():
#     """Tests loading a PDB with multiple models, expecting a warning and first model."""
#     multi_model_file = TEST_DATA_DIR / "multi_model_protein.pdb" # Create this file
#     if not multi_model_file.is_file():
#          pytest.skip(f"Multi-model test file not found at {multi_model_file}")
#
#     with pytest.warns(UserWarning, match="multiple models"):
#         atom_array = readers.load_structure(multi_model_file)
#
#     assert isinstance(atom_array, struc.AtomArray)
#     assert len(atom_array) == EXPECTED_ATOMS_MODEL_1 # Define this

# @pytest.mark.skip(reason="Test file not yet created")
# def test_load_corrupt_file():
#     """Tests loading a deliberately corrupted PDB/CIF file."""
#     # corrupt_file = TEST_DATA_DIR / "corrupt_structure.pdb" # Create this file
#     # with pytest.raises((ValueError, BadStructureError)):
#     #     readers.load_structure(corrupt_file)
#     pass