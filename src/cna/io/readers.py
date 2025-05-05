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
    Loads a molecular structure from a PDB or mmCIF file using Biotite.

    If the file contains multiple models (AtomArrayStack), only the first
    model is returned.

    Args:
        file_path: The path to the PDB or mmCIF file.

    Returns:
        A biotite.AtomArray representing the first model in the structure file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file cannot be parsed or is an unknown format.
        BadStructureError: If Biotite encounters structural inconsistencies.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Structure file not found: {file_path}")

    try:
        # Biotite's load_structure handles file type detection (PDB/CIF)
        # and can return AtomArray or AtomArrayStack
        structure = strucio.load_structure(str(file_path))

        if isinstance(structure, struc.AtomArray):
            logger.info(f"Loaded structure with {len(structure)} atoms from {file_path}.")
            return structure
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
            # This case should ideally not be reached with PDB/CIF and load_structure
            raise ValueError(f"Unexpected structure type loaded from {file_path}: {type(structure)}")

    except BadStructureError as e:
        logger.error(f"Biotite structural error parsing {file_path}: {e}")
        raise BadStructureError(f"Biotite structural error parsing {file_path}: {e}") from e
    except Exception as e:
        # Catch other potential Biotite/IO errors during parsing
        logger.error(f"Failed to parse structure file {file_path}: {e}")
        raise ValueError(f"Failed to parse structure file {file_path}: {e}") from e
