import numpy as np
import numpy.typing as npt
import biotite.structure as struc

class MolecularSystem:
    """
    Represents a molecular system, wrapping a Biotite AtomArray.

    Provides convenient access to common structural properties.
    """

    def __init__(self, atom_array: struc.AtomArray) -> None:
        """
        Initializes the MolecularSystem.

        Args:
            atom_array: A Biotite AtomArray representing the system's structure.
                        It is assumed this contains only a single model.
        """
        if not isinstance(atom_array, struc.AtomArray):
            raise TypeError(
                "Input must be a biotite.AtomArray, not "
                f"{type(atom_array).__name__}"
            )
        self._atom_array: struc.AtomArray = atom_array

    @property
    def atom_count(self) -> int:
        """
        Returns the total number of atoms in the system.
        """
        return len(self._atom_array)

    @property
    def coords(self) -> npt.NDArray[np.float32]:
        """
        Returns the atomic coordinates as a NumPy array.

        Shape: (n_atoms, 3)
        """
        return self._atom_array.coord

    @property
    def atom_array(self) -> struc.AtomArray:
        """
        Provides direct access to the underlying Biotite AtomArray.
        """
        return self._atom_array

    def __len__(self) -> int:
        """
        Returns the number of atoms in the system.
        """
        return self.atom_count

    def __repr__(self) -> str:
        """
        Returns a string representation of the MolecularSystem.
        """
        return f"<MolecularSystem ({self.atom_count} atoms)>"
