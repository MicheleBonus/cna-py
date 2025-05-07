      
# tests/test_cli.py
"""
Unit tests for the cna.cli module.
"""

import argparse
import logging
from pathlib import Path
# Mock importlib.metadata if the package isn't installed during testing
from unittest.mock import patch

import pytest

from cna import cli, config

# Load default config once for all tests in this module
DEFAULT_CFG = config.load_default_config()
# Define a dummy version for tests where the package might not be installed
DUMMY_VERSION = "0.1.0-test"

@pytest.fixture(autouse=True)
def mock_metadata_version():
    """Fixture to automatically mock importlib.metadata.version."""
    # Use the package name defined in cli._get_version
    package_name = "cna-py"
    with patch('importlib.metadata.version', return_value=DUMMY_VERSION) as mock_ver:
        yield mock_ver

def test_cli_basic_required_args(mock_metadata_version):
    """Test parsing with only the required input argument."""
    parser = cli._build_parser(DEFAULT_CFG)
    cmd_args = ['-i', 'input.pdb']
    args = parser.parse_args(cmd_args)

    assert args.input == 'input.pdb'
    # Check defaults for optional arguments
    assert args.res_dir == DEFAULT_CFG.output.result_dir
    assert args.verbose == DEFAULT_CFG.output.verbosity_level
    assert args.stbmap is False # Default for stbmap in config is False

def test_cli_with_optional_args(mock_metadata_version):
    """Test parsing with several optional arguments provided."""
    parser = cli._build_parser(DEFAULT_CFG)
    test_output_dir = "custom_output"
    cmd_args = [
        '--input', 'structure.cif',
        '--res_dir', test_output_dir,
        '--stbmap',
        '-vv'
    ]
    args = parser.parse_args(cmd_args)

    assert args.input == 'structure.cif'
    assert args.res_dir == test_output_dir
    assert args.stbmap is True
    # argparse adds counts to the default value provided
    assert args.verbose == DEFAULT_CFG.output.verbosity_level + 2

def test_cli_verbosity_levels(mock_metadata_version):
    """Test different verbosity levels using -v flags."""
    parser = cli._build_parser(DEFAULT_CFG)

    # No verbosity flag -> should use default from config
    args_default = parser.parse_args(['-i', 'f.pdb'])
    assert args_default.verbose == DEFAULT_CFG.output.verbosity_level

    # -v -> default + 1
    args_v1 = parser.parse_args(['-i', 'f.pdb', '-v'])
    assert args_v1.verbose == DEFAULT_CFG.output.verbosity_level + 1

    # -vvv -> default + 3
    args_v3 = parser.parse_args(['-i', 'f.pdb', '-vvv'])
    assert args_v3.verbose == DEFAULT_CFG.output.verbosity_level + 3

def test_cli_missing_required_arg(mock_metadata_version):
    """Test that omitting the required -i argument causes SystemExit."""
    parser = cli._build_parser(DEFAULT_CFG)
    cmd_args = ['--res_dir', 'out'] # Missing -i/--input

    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(cmd_args)
    # Check that it exited with an error code (usually 2 for argparse errors)
    assert excinfo.value.code != 0

def test_cli_invalid_arg(mock_metadata_version):
    """Test that providing an unrecognized argument causes SystemExit."""
    parser = cli._build_parser(DEFAULT_CFG)
    cmd_args = ['-i', 'in.pdb', '--nonexistent-option']

    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(cmd_args)
    assert excinfo.value.code != 0

def test_cli_version_action(mock_metadata_version):
    """Test that the --version flag triggers the version action and exits."""
    parser = cli._build_parser(DEFAULT_CFG)
    cmd_args = ['--version']

    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(cmd_args)
    # Version action typically exits with code 0
    assert excinfo.value.code == 0
    # Check that the mock was called
    mock_metadata_version.assert_called_once_with("cna-py")


def test_main_function_entry_point(caplog, tmp_path, mock_metadata_version):
    """Test the main() function execution path with basic arguments."""
    test_input = tmp_path / "input.pdb"
    test_input.touch() # Create a dummy input file
    test_output = tmp_path / "cli_test_out"

    # Command line args as a list of strings
    test_argv = ['-i', str(test_input), '--res_dir', str(test_output), '-v', '--stbmap']

    # Capture logging output
    caplog.set_level(logging.DEBUG)

    # Expect SystemExit(0) for a successful run that calls sys.exit(0)
    with pytest.raises(SystemExit) as excinfo:
        cli.main(test_argv)
    assert excinfo.value.code == 0

    # Check log messages (more robustly)
    assert f"Starting CNA v{DUMMY_VERSION}" in caplog.text

    # --- MODIFICATION START: Check for key parts instead of exact repr ---
    # Check that the "Parsed arguments" message exists at DEBUG level
    parsed_args_log_found = any(
        "Parsed arguments: Namespace(" in record.message for record in caplog.records if record.levelno == logging.DEBUG
    )
    assert parsed_args_log_found, "Log message for Parsed arguments not found at DEBUG level"

    # Check for the key argument values within the captured text
    # Use repr() to handle potential backslash escaping issues on Windows paths
    assert f"input={repr(str(test_input))}" in caplog.text
    assert f"res_dir={repr(str(test_output))}" in caplog.text
    expected_verbose_count = DEFAULT_CFG.output.verbosity_level + 1
    assert f"verbose={expected_verbose_count}" in caplog.text
    assert "stbmap=True" in caplog.text
    # --- MODIFICATION END ---

    # Check other important logs
    assert "Effective logging level: DEBUG" in caplog.text
    assert "CLI parsing complete." in caplog.text
    assert f"Input structure: {test_input.resolve()}" in caplog.text
    assert f"Output directory: {test_output.resolve()}" in caplog.text
    assert "Workflow execution would start here." in caplog.text
    assert "CNA run finished" in caplog.text

def test_main_function_handles_argparse_exit(caplog, mock_metadata_version):
    """Test that main() catches SystemExit from argparse (e.g., --help)."""
    test_argv_help = ['--help']
    test_argv_error = ['--res_dir', 'out'] # Missing -i

    with pytest.raises(SystemExit) as excinfo_help:
        cli.main(test_argv_help)
    assert excinfo_help.value.code == 0 # --help should exit cleanly

    with pytest.raises(SystemExit) as excinfo_error:
        cli.main(test_argv_error)
    assert excinfo_error.value.code != 0 # Missing required arg is an error
