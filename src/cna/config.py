# src/cna/config.py
"""
Configuration dataclasses for the Constraint Network Analysis (CNA) package.

Defines the structure for simulation, constraint, analysis, and output
parameters using dataclasses, and provides default values based on legacy CNA.
"""

import dataclasses
from typing import List, Optional, Tuple
from dataclasses import field

# Using frozen=True makes instances immutable after creation, which is
# generally desirable for configuration objects.
@dataclasses.dataclass(frozen=True)
class SimulationParams:
    """Parameters controlling the simulation process."""
    e_stop: float = -7.0  # HB energy cutoff stop value (kcal/mol) [Original: E_STOP]
    e_start: float = -0.25 # HB energy cutoff start value (kcal/mol) [Original: E_START]
    e_step: Optional[float] = None # HB energy cutoff step. None means adaptive steps [Original: E_STEP]
    tus_type: int = 1 # Thermal Unfolding Simulation type (1 or 2) [Original: TUS]
                      # 1: Constant hydrophobic constraints
                      # 2: Temperature-dependent hydrophobic constraints
    fnc_steps: int = 100 # Number of network topologies for FNC ensemble [Original: F_STEPS]
    cores: int = 1 # Number of CPU cores to use for parallel processing [Original: CORES]

@dataclasses.dataclass(frozen=True)
class ConstraintParams:
    """Parameters defining how constraints are generated."""
    hp_fxn: int = 1 # Method for placing hydrophobic tethers (0, 1, 2, 3) [Original: HP_FXN]
                    # 0: None, 1: Max, 2: Medium, 3: Min
    # Default constant cutoff for TUS_TYPE=1 [Original: C_START]
    c_cutoff_const: float = 0.25
    # Default start/stop range for TUS_TYPE=2 [Original: C_START, C_STOP]
    c_cutoff_range: Tuple[float, float] = (0.25, 0.35)
    # NOTE: Logic to select between c_cutoff_const and c_cutoff_range based on
    # SimulationParams.tus_type will be handled during constraint generation.

@dataclasses.dataclass(frozen=True)
class AnalysisParams:
    """Parameters controlling post-simulation analysis."""
    # Cutoff for considering residues with dG_i,CNA > value [Original: CUT]
    dG_cutoff: float = 0.2
    # Cutoff distance for native contact identification [Original: NCD]
    native_contact_distance: float = 5.0
    # Minimum size of a cluster to be considered percolated [Original: MIN_CLUSTER_SIZE_PERCOLATED]
    min_cluster_size_percolated: int = 30
    # Methods for phase transition detection [Original: TRANSITION_SOURCE]
    transition_source: List[str] = field(default_factory=lambda: ["cce2_sigmoid", "cce2_spline"])
    # Cutoff distance for unfolding nuclei identification type 4 [Original: NEIGHBOR_CUTOFF_UNF]
    neighbor_cutoff_unfolding: float = 5.0
    # Akaike information criteria for transition fitting [Original: --aic]
    aic_selection: bool = False
    # Types of unfolding nuclei identification methods to use [Original: --unfolding_nuclei]
    # 1: Largest rigid cluster becoming flexible
    # 2: All rigid clusters (>= min_cluster_size_percolated) becoming flexible
    # 3: Residues making critical hydrogen bonds breaking
    # 4: Residues around critical hydrogen bond atoms (within neighbor_cutoff_unfolding)
    unfolding_nuclei_types: Optional[List[int]] = None # e.g., [1, 2, 3, 4] if specified

@dataclasses.dataclass(frozen=True)
class OutputParams:
    """Parameters controlling output generation."""
    result_dir: str = "results" # Name of the results directory [Original: --res_dir]
    stbmap: bool = False # Write stability map matrix file [Original: --stbmap]
    netout: bool = False # Write FIRST network file [Original: --netout]
    # Write individual results for each ensemble member [Original: --all_results]
    all_results: bool = False
    verbosity_level: int = 1 # Verbosity level (0-3) [Original: --verbose]

@dataclasses.dataclass(frozen=True)
class CNAConfig:
    """Main configuration object holding parameters for a CNA run."""
    simulation: SimulationParams = field(default_factory=SimulationParams)
    constraints: ConstraintParams = field(default_factory=ConstraintParams)
    analysis: AnalysisParams = field(default_factory=AnalysisParams)
    output: OutputParams = field(default_factory=OutputParams)

    # Potentially add top-level flags if they don't fit neatly elsewhere
    # web_interface_mode: bool = False # Example if needed later

def load_default_config() -> CNAConfig:
    """
    Instantiates and returns the default CNA configuration settings.

    Returns:
        An immutable CNAConfig object populated with default parameter values.
    """
    return CNAConfig()

# Example usage (optional, for quick testing if run directly)
if __name__ == "__main__":
    default_config = load_default_config()
    print("Default CNA Configuration:")
    print(default_config)
    print("\nSimulation Parameters:")
    print(default_config.simulation)
    print("\nConstraint Parameters:")
    print(default_config.constraints)
    print("\nAnalysis Parameters:")
    print(default_config.analysis)
    print("\nOutput Parameters:")
    print(default_config.output)

    # Accessing a specific value
    print(f"\nDefault E_START: {default_config.simulation.e_start}")