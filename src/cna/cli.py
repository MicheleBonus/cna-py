# src/cna/cli.py
"""
Command-line interface for the Constraint Network Analysis (CNA) package.

Handles argument parsing and initiates the analysis workflow.
"""

import argparse
import logging
import sys
from importlib import metadata
from pathlib import Path
from typing import List, Optional, Sequence

from cna.config import CNAConfig, load_default_config

# Setup logger for this module - configuration will be done in main()
logger = logging.getLogger(__name__)
# Get the root logger instance to configure its level in main()
# Ensures configuration affects handlers potentially added by pytest (caplog)
root_logger = logging.getLogger()


def _get_version() -> str:
    """Retrieves the package version using importlib.metadata."""
    try:
        # Ensure this matches the package name used during installation (e.g., in pyproject.toml)
        return metadata.version("cna-py")
    except metadata.PackageNotFoundError:
        # Provide a fallback version for development environments where the package isn't installed
        return "0.0.0-dev"


def _build_parser(default_cfg: CNAConfig) -> argparse.ArgumentParser:
    """
    Builds the argument parser for the CNA CLI.

    Args:
        default_cfg: The default configuration object.

    Returns:
        An configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Constraint Network Analysis (CNA): Analyze biomolecular "
                    "flexibility and rigidity.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="cna-run" # Match the intended entry point name
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}", # Use dynamic version retrieval
        help="Show program's version number and exit.",
    )

    # --- Input/Output Arguments ---
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        metavar="FILE",
        help="Input structure file path (e.g., PDB, mmCIF).",
    )
    parser.add_argument(
        "--res_dir",
        type=str,
        # Set the default value displayed in help message from config
        default=default_cfg.output.result_dir,
        metavar="DIR",
        help="Output results directory.",
    )

    # --- Simulation/Workflow Arguments (Placeholders for now) ---

    # --- Analysis Arguments (Placeholders for now) ---

    # --- Output Control Arguments ---
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        # Set the internal default count based on the config's level
        default=default_cfg.output.verbosity_level,
        help=f"Increase output verbosity. No flag: Default level from config "
             f"({logging.getLevelName(logging.WARNING + (10 * (1-default_cfg.output.verbosity_level))) if default_cfg.output.verbosity_level <= 1 else 'DEBUG'}), "
             f"-v: {logging.getLevelName(logging.INFO)}, -vv: {logging.getLevelName(logging.DEBUG)}. "
             f"Default verbosity level set to {default_cfg.output.verbosity_level} in config.",
    )

    # Handle boolean flags like --stbmap correctly with config defaults
    # Standard argparse: default for store_true is False. Flag presence sets it True.
    # We'll apply the config default *after* parsing if the flag wasn't used.
    parser.add_argument(
        "--stbmap",
        action="store_true",
        help="Write stability map matrix file.",
    )
    # Ensure argparse knows the default state is False if the flag isn't given
    parser.set_defaults(stbmap=False)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    """
    Main entry point for the CNA command-line interface.

    Parses arguments, sets up logging, and calls the appropriate workflow.

    Args:
        argv: Optional sequence of command-line arguments. If None, uses sys.argv[1:].
    """
    # Basic logging setup in case of early errors (e.g., config loading)
    # This might be overridden later but ensures early messages are seen.
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    if argv is None:
        argv = sys.argv[1:] # Use command-line arguments if not provided directly

    # Load default configuration first
    try:
        default_cfg = load_default_config()
    except Exception as e:
        logger.error(f"Failed to load default configuration: {e}", exc_info=True)
        sys.exit(1)

    # Build the parser using defaults for help messages
    parser = _build_parser(default_cfg)

    # Parse the arguments
    try:
        args = parser.parse_args(args=argv)
    except SystemExit as e:
        # Catch argparse exit (e.g., due to --help or errors) and exit gracefully
        sys.exit(e.code)

    # --- Configure Logging based on verbosity ---
    # Map verbosity count to logging levels. The 'count' action adds to the default.
    # Example: default_cfg.output.verbosity_level = 1 (INFO)
    #   No flag -> args.verbose = 1 -> INFO level
    #   -v      -> args.verbose = 2 -> DEBUG level
    #   -vv     -> args.verbose = 3 -> DEBUG level
    log_level = logging.WARNING  # Base level
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG

    # Configure the *root* logger's level. This allows pytest's caplog to work.
    root_logger.setLevel(log_level)

    # Define a standard formatter
    log_formatter = logging.Formatter(
         "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
         datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Ensure there's at least one handler (e.g., for stdout/stderr)
    # and apply the formatter. If pytest is running, caplog adds handlers.
    if not root_logger.hasHandlers():
         # Add a default handler if running standalone (not via pytest)
         stream_handler = logging.StreamHandler(sys.stderr)
         root_logger.addHandler(stream_handler)

    # Apply the formatter to all existing handlers
    for handler in root_logger.handlers:
         handler.setFormatter(log_formatter)

    # --- Log startup messages ---
    logger.info(f"Starting CNA v{_get_version()}")
    logger.debug(f"Raw command line arguments: {argv}")
    logger.debug(f"Parsed arguments: {args}")
    logger.debug(f"Effective logging level: {logging.getLevelName(log_level)}")
    logger.debug(f"Output directory set to: {args.res_dir}")

    # Apply config default for stbmap *after* parsing if CLI flag wasn't used
    stbmap_enabled = args.stbmap or default_cfg.output.stbmap
    if stbmap_enabled:
        logger.debug("Stability map output enabled.")


    # --- Process Paths and Check Existence ---
    logger.info("CLI parsing complete.")
    try:
        input_path = Path(args.input)
        if not input_path.is_file(): # Check if it's a file that exists
             logger.error(f"Input is not a valid file: {input_path}")
             sys.exit(1) # Exit if input file doesn't exist

        output_dir = Path(args.res_dir)
        # Create output directory if it doesn't exist
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured output directory exists: {output_dir.resolve()}")
        except OSError as e:
            logger.error(f"Could not create output directory {output_dir}: {e}", exc_info=True)
            sys.exit(1)

        logger.info(f"Input structure: {input_path.resolve()}")
        logger.info(f"Output directory: {output_dir.resolve()}")
    except Exception as e:
        logger.error(f"Error processing file paths: {e}", exc_info=True)
        sys.exit(1)


    # --- Placeholder for Workflow Execution ---
    logger.info("Placeholder: Workflow execution would start here.")
    # Future: Pass 'args' or a merged config object to the workflow
    # run_workflow(args=args, default_config=default_cfg)


    logger.info("CNA run finished (placeholder).")
    # Explicitly exit successfully if main completes without error
    sys.exit(0)


if __name__ == "__main__":
    # Allows direct execution for development
    main()