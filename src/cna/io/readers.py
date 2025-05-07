import logging
from pathlib import Path
from typing import Union

import biotite.structure as struc
import biotite.structure.io as strucio
from biotite.structure.error import BadStructureError

# Setup logger for this module
logger = logging.getLogger(__name__)

def load_structure(file_path: Union[str, Path]) -> struc.AtomArray:
    """
    Loads a molecular structure from a PDB or mmCIF file.

    This function utilizes Biotite to parse the structure file. If the file
    contains multiple models (as an AtomArrayStack), only the first model
    is extracted and returned as an AtomArray.

    Args:
        file_path: The path to the PDB or mmCIF file. The path can be
            provided as a string or a Path object.

    Returns:
        A biotite.AtomArray representing the first model in the structure file.

    Raises:
        FileNotFoundError: If the specified file does not exist at the given path.
        ValueError: If the file cannot be parsed by Biotite, is an unknown
            format, or if an unexpected structure type is loaded.
        BadStructureError: If Biotite encounters inconsistencies or errors
            within the structure of the file.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Structure file not found: {file_path}")

    # Try-except block to handle potential parsing errors when loading the structure
    try:
        # Biotite's load_structure handles file type detection; currently supports:
        # .pdb, .pdbqt, .cif, .pdbx, .bcif, .gro, .mol2, .sdf, .trr, .xtc, .dcd, .netcdf
        # and can return AtomArray or AtomArrayStack
        structure = strucio.load_structure(str(file_path))

        # If the structure only has one model, it should be an AtomArray, so we can return it directly
        if isinstance(structure, struc.AtomArray):
            logger.info(f"Loaded structure with {len(structure)} atoms from {file_path}.")
            return structure
        # If the structure has multiple models, we extract the first one and log a warning
        elif isinstance(structure, struc.AtomArrayStack):
            if structure.stack_depth() > 1:
                logger.warning(
                    f"File {file_path} contains multiple models ({structure.stack_depth()}). "
                    f"Using the first model only."
                )
            first_model = structure[0]
            logger.info(f"Loaded first model with {len(first_model)} atoms from {file_path}.")
            return first_model
        else:
            # This case should never happen if an expected file type (see above) is provided
            # TODO: write a test for all file types with the respective valid contents.
            # Since load_structure does not check contents but only the file extension,
            # we rely on the user to provide files with the correct extension.
            # TODO: (optional) implement a check based on the file contents (cave: performance).
            raise ValueError(f"Unexpected structure type loaded from {file_path}: {type(structure)}")

    except BadStructureError as e:
        # This is biotite's specific error for structural inconsistencies
        # TODO: write a test that raises this error
        logger.error(f"Biotite structural error parsing {file_path}: {e}")
        raise BadStructureError(f"Biotite structural error parsing {file_path}: {e}") from e
    except Exception as e:
        # Catch other potential Biotite/IO errors during parsing
        # TODO: write a test that raises this error
        logger.error(f"Failed to parse structure file {file_path}: {e}")
        raise ValueError(f"Failed to parse structure file {file_path}: {e}") from e