import numpy as np
import numpy.typing as npt
import biotite.structure as struc

class MolecularSystem:
    """Represents a molecular system, wrapping a Biotite AtomArray.

    This class provides a convenient interface to access common structural
    properties from an underlying Biotite AtomArray. It assumes that the
    provided AtomArray represents a single structural model.
    """

    def __init__(self, atom_array: struc.AtomArray) -> None:
        """Initializes the MolecularSystem with a Biotite AtomArray.

        Args:
            atom_array: A Biotite AtomArray representing the system's
                structure. It is assumed this contains only a single model.
        """
        if not isinstance(atom_array, struc.AtomArray):
            raise TypeError(
                f"Input must be a biotite.AtomArray, not "
                f"{type(atom_array).__name__}"
            )
        self._atom_array: struc.AtomArray = atom_array

    @property
    def atom_count(self) -> int:
        """The total number of atoms in the system."""
        return len(self._atom_array)

    @property
    def coords(self) -> npt.NDArray[np.float32]:
        """The atomic coordinates of the system.

        Returns:
            A NumPy array of shape (N, 3) containing the atomic
            coordinates, where N is the number of atoms. Each row
            corresponds to an atom, and columns store the x, y, and z
            coordinates.
        """
        return self._atom_array.coord

    @property
    def atom_array(self) -> struc.AtomArray:
        """The underlying Biotite AtomArray instance."""
        return self._atom_array

    def __len__(self) -> int:
        """Return the number of atoms in the system.

        This allows `len()` to be called on a MolecularSystem instance,
        mirroring the atom_count.
        """
        return self.atom_count

    def __repr__(self) -> str:
        """Return a string representation of the MolecularSystem.

        The representation is in the format '<MolecularSystem (N atoms)>'.
        """
        return f"<MolecularSystem ({self.atom_count} atoms)>"