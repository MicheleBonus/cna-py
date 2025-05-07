# tests/test_config.py
"""
Unit tests for the CNA configuration module (cna.config).
"""

import pytest
import dataclasses
from typing import Optional, List, Tuple

# Import the items to be tested from src/cna/config.py
from cna.config import (
    CNAConfig,
    SimulationParams,
    ConstraintParams,
    AnalysisParams,
    OutputParams,
    load_default_config
)

def test_default_config_loading():
    """Verify that load_default_config returns a valid CNAConfig object."""
    config = load_default_config()

    assert isinstance(config, CNAConfig)
    assert isinstance(config.simulation, SimulationParams)
    assert isinstance(config.constraints, ConstraintParams)
    assert isinstance(config.analysis, AnalysisParams)
    assert isinstance(config.output, OutputParams)

    # Verify immutability (frozen=True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        # Attempt to modify a field (should fail if frozen)
        # pylint: disable=assigning-non-slot # Pylint doesn't know about frozen dataclasses
        config.simulation.cores = 2 # type: ignore

def test_default_simulation_params():
    """Verify default values within the SimulationParams dataclass."""
    config = load_default_config()
    sim_params = config.simulation

    assert sim_params.e_stop == -7.0
    assert isinstance(sim_params.e_stop, float)

    assert sim_params.e_start == -0.25
    assert isinstance(sim_params.e_start, float)

    assert sim_params.e_step is None
    assert isinstance(sim_params.e_step, type(None)) # Check Optional type correctly defaults to None

    assert sim_params.tus_type == 1
    assert isinstance(sim_params.tus_type, int)

    assert sim_params.fnc_steps == 100
    assert isinstance(sim_params.fnc_steps, int)

    assert sim_params.cores == 1
    assert isinstance(sim_params.cores, int)

def test_default_constraint_params():
    """Verify default values within the ConstraintParams dataclass."""
    config = load_default_config()
    cons_params = config.constraints

    assert cons_params.hp_fxn == 1
    assert isinstance(cons_params.hp_fxn, int)

    assert cons_params.c_cutoff_const == 0.25
    assert isinstance(cons_params.c_cutoff_const, float)

    assert cons_params.c_cutoff_range == (0.25, 0.35)
    assert isinstance(cons_params.c_cutoff_range, tuple)
    assert len(cons_params.c_cutoff_range) == 2
    assert isinstance(cons_params.c_cutoff_range[0], float)
    assert isinstance(cons_params.c_cutoff_range[1], float)

def test_default_analysis_params():
    """Verify default values within the AnalysisParams dataclass."""
    config = load_default_config()
    analysis_params = config.analysis

    assert analysis_params.dG_cutoff == 0.2
    assert isinstance(analysis_params.dG_cutoff, float)

    assert analysis_params.native_contact_distance == 5.0
    assert isinstance(analysis_params.native_contact_distance, float)

    assert analysis_params.min_cluster_size_percolated == 30
    assert isinstance(analysis_params.min_cluster_size_percolated, int)

    assert analysis_params.transition_source == ["cce2_sigmoid", "cce2_spline"]
    assert isinstance(analysis_params.transition_source, list)
    assert all(isinstance(s, str) for s in analysis_params.transition_source)

    assert analysis_params.neighbor_cutoff_unfolding == 5.0
    assert isinstance(analysis_params.neighbor_cutoff_unfolding, float)

    assert analysis_params.aic_selection is False
    assert isinstance(analysis_params.aic_selection, bool)

    assert analysis_params.unfolding_nuclei_types is None
    assert isinstance(analysis_params.unfolding_nuclei_types, type(None))

def test_default_output_params():
    """Verify default values within the OutputParams dataclass."""
    config = load_default_config()
    output_params = config.output

    assert output_params.result_dir == "results"
    assert isinstance(output_params.result_dir, str)

    assert output_params.stbmap is False
    assert isinstance(output_params.stbmap, bool)

    assert output_params.netout is False
    assert isinstance(output_params.netout, bool)

    assert output_params.all_results is False
    assert isinstance(output_params.all_results, bool)

    assert output_params.verbosity_level == 1
    assert isinstance(output_params.verbosity_level, int)