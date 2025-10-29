"""
Helper functions for Snakefile resource declaration.

This module provides utilities for extracting Snakemake resources from
esm_runscripts configuration files. Users import and call get_resources()
in their Snakefiles to automatically determine resource requirements.

Example Usage in Snakefile
---------------------------
In your Snakefile::

    from esm_runscripts.helper import get_resources

    rule compute_phase:
        params:
            runscript="awicm.yaml",
            task="compute",
            expid="exp001"
        resources:
            **get_resources("awicm.yaml", "compute", expid="exp001")
        wrapper:
            "file://path/to/esm_runscripts"
"""

__author__ = "Paul Gierz"
__copyright__ = "Copyright 2025, Paul Gierz"
__email__ = "paul.gierz@awi.de"
__license__ = "MIT"

import os
import re
import subprocess
import sys
import warnings
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

try:
    import herrkunft as yaml
except ImportError:
    # Fallback to PyYAML if herrkunft not available
    import yaml


class Task(str, Enum):
    """Valid esm_runscripts task types."""
    PREPCOMPUTE = "prepcompute"
    COMPUTE = "compute"
    TIDY = "tidy"
    POST = "post"


def get_resources(
    runscript: Union[str, Path],
    task: Union[str, Task],
    expid: str = "test",
    modify_config: Optional[Union[str, Path]] = None,
    base_dir: Optional[Union[str, Path]] = None,
    **extra_args,
) -> Dict[str, Union[int, str]]:
    """
    Extract Snakemake resources by running esm_runscripts --check.

    This function runs esm_runscripts in check mode to generate the
    finished_config.yaml file, then parses it to extract resource
    requirements for Snakemake.

    Parameters
    ----------
    runscript : str or Path
        Path to ESM runscript YAML file
    task : str or Task
        Phase to execute (prepcompute/compute/tidy/post)
    expid : str, default="test"
        Experiment ID
    modify_config : str or Path, optional
        Path to config override file
    base_dir : str or Path, optional
        Base directory for experiment (default: current directory)
    **extra_args
        Additional arguments passed to esm_runscripts

    Returns
    -------
    dict
        Dictionary with Snakemake resource keys:

        - nodes : int
            Number of compute nodes
        - tasks : int
            Number of tasks/cores
        - mem_mb : int
            Memory in megabytes
        - runtime : int
            Runtime in minutes
        - partition : str, optional
            SLURM partition name
        - account : str, optional
            SLURM account

    Raises
    ------
    FileNotFoundError
        If runscript doesn't exist
    subprocess.CalledProcessError
        If esm_runscripts --check fails
    ValueError
        If finished_config.yaml cannot be parsed

    Examples
    --------
    Basic usage with string paths::

        resources = get_resources("awicm.yaml", "compute", expid="exp001")

    Using Path objects and Task enum::

        resources = get_resources(Path("config.yaml"), Task.COMPUTE)

    With additional configuration::

        resources = get_resources(
            "awicm.yaml",
            "compute",
            expid="exp001",
            modify_config="overrides.yaml",
            base_dir="/path/to/experiments"
        )
    """
    # Validate runscript exists
    runscript_path = Path(runscript).resolve()
    if not runscript_path.exists():
        raise FileNotFoundError(f"Runscript not found: {runscript}")

    # Convert task to string if it's an Enum
    task_str = task.value if isinstance(task, Task) else str(task)

    # Validate and convert base_dir
    if base_dir is not None:
        base_dir_path = Path(base_dir).resolve()
        if not base_dir_path.exists():
            raise FileNotFoundError(f"Base directory not found: {base_dir}")
        if not base_dir_path.is_dir():
            raise NotADirectoryError(f"Base directory is not a directory: {base_dir}")
        cwd = str(base_dir_path)
    else:
        cwd = os.getcwd()

    # Build command
    cmd = [
        "esm_runscripts",
        "--check",
        str(runscript_path),
        "-t",
        task_str,
        "-e",
        expid,
    ]

    if modify_config:
        cmd.extend(["-m", str(modify_config)])

    # Add any extra arguments
    for key, value in extra_args.items():
        cmd.extend([f"--{key}", str(value)])

    # Run esm_runscripts --check to generate finished_config.yaml
    print(f"Extracting resources: {' '.join(cmd)}", file=sys.stderr)

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, cwd=cwd
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running esm_runscripts --check:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        raise

    # Find and load finished_config.yaml
    config_path = _find_finished_config(expid, task, base_dir)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Extract and return resources
    resources = _extract_resources_from_config(config)

    print(f"Extracted resources: {resources}", file=sys.stderr)

    return resources


def _find_finished_config(
    expid: str, task: str, base_dir: Optional[str] = None
) -> Path:
    """
    Locate the finished_config.yaml file generated by esm_runscripts.

    Parameters
    ----------
    expid : str
        Experiment ID
    task : str
        Task/phase name
    base_dir : str, optional
        Optional base directory to search

    Returns
    -------
    Path
        Path to finished_config.yaml

    Raises
    ------
    FileNotFoundError
        If config file cannot be found
    """
    search_dir = Path(base_dir) if base_dir else Path.cwd()

    # Pattern: {expid}_finished_config.yaml or {expid}_{model}_finished_config.yaml
    # Search in common locations:
    # 1. {base_dir}/{expid}/config/
    # 2. {base_dir}/config/
    # 3. Current directory

    search_paths = [
        search_dir / expid / "config",
        search_dir / "config",
        search_dir,
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Try exact match first
        exact_match = search_path / f"{expid}_finished_config.yaml"
        if exact_match.exists():
            return exact_match

        # Try pattern match (for coupled models)
        pattern = f"{expid}_*finished_config.yaml"
        matches = list(search_path.glob(pattern))

        if matches:
            # Return the most recent one
            if len(matches) > 1:
                warnings.warn(
                    f"Found {len(matches)} finished_config.yaml files for expid={expid}. "
                    f"Using the most recently modified one. This may not be correct if you "
                    f"have been manually examining or modifying these files.",
                    UserWarning,
                    stacklevel=3
                )
            return max(matches, key=lambda p: p.stat().st_mtime)

    # Build list of searched paths for error message
    searched_paths = "\n  ".join(str(p) for p in search_paths)
    raise FileNotFoundError(
        f"Could not find finished_config.yaml for expid={expid}.\n"
        f"Searched in the following locations:\n  {searched_paths}"
    )


def _extract_resources_from_config(config: dict) -> Dict[str, int]:
    """
    Extract Snakemake resources from finished_config.yaml.

    Parameters
    ----------
    config : dict
        Parsed YAML configuration dict

    Returns
    -------
    dict
        Dictionary with Snakemake resource specifications

    Notes
    -----
    This function does not provide default values for missing resource
    specifications. If a value is not specified in the configuration,
    the corresponding key will not be present in the returned dictionary,
    allowing SLURM to use its own defaults or raise an error if required
    parameters are missing.
    """
    general = config.get("general", {})
    computer = config.get("computer", {})

    resources = {}

    # Only add resources that are explicitly specified
    if "resubmit_nodes" in general:
        resources["nodes"] = general["resubmit_nodes"]

    if "resubmit_tasks" in general:
        resources["tasks"] = general["resubmit_tasks"]

    if "memory_per_task" in computer:
        resources["mem_mb"] = _parse_memory(computer["memory_per_task"])

    if "run_time" in general:
        resources["runtime"] = _parse_time(general["run_time"])

    # Add partition if specified
    if "partition" in computer:
        resources["partition"] = computer["partition"]

    # Add account if specified
    if "account" in computer:
        resources["account"] = computer["account"]

    return resources


def _parse_memory(mem_str: str) -> int:
    """
    Convert memory string to megabytes.

    Parameters
    ----------
    mem_str : str
        Memory specification (e.g., "200G", "180000M", "1024K")

    Returns
    -------
    int
        Memory in megabytes, with a minimum of 1 MB

    Examples
    --------
    >>> _parse_memory("200G")
    204800
    >>> _parse_memory("1024M")
    1024
    >>> _parse_memory("512K")
    1
    """
    if isinstance(mem_str, (int, float)):
        return int(mem_str)

    mem_str = str(mem_str).strip().upper()

    # Match number and unit
    match = re.match(r"([0-9.]+)\s*([KMGT]?B?)", mem_str)
    if not match:
        raise ValueError(f"Cannot parse memory: {mem_str}")

    value = float(match.group(1))
    unit = match.group(2)

    # Convert to MB
    if unit.startswith("K"):
        # Round up to at least 1 MB
        mb_value = value / 1024
        return max(1, int(mb_value + 0.5))
    elif unit.startswith("M") or not unit:
        return int(value)
    elif unit.startswith("G"):
        return int(value * 1024)
    elif unit.startswith("T"):
        return int(value * 1024 * 1024)
    else:
        raise ValueError(f"Unknown memory unit: {unit}")


def _parse_time(time_str: str) -> int:
    """
    Convert time string to minutes.

    Parameters
    ----------
    time_str : str
        Time specification (HH:MM:SS or minutes)

    Returns
    -------
    int
        Time in minutes

    Examples
    --------
    >>> _parse_time("12:00:00")
    720
    >>> _parse_time("01:30:00")
    90
    >>> _parse_time("720")
    720
    """
    if isinstance(time_str, (int, float)):
        return int(time_str)

    time_str = str(time_str).strip()

    # Try parsing as integer (already in minutes)
    try:
        return int(time_str)
    except ValueError:
        pass

    # Parse HH:MM:SS or MM:SS format
    parts = time_str.split(":")

    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 60 + minutes + (1 if seconds > 0 else 0)
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes + (1 if seconds > 0 else 0)
    else:
        raise ValueError(f"Cannot parse time: {time_str}")


# Wrapper execution functions


def find_run_script(expid: str, task: str, base_dir: Path = None) -> Path:
    """
    Locate the generated .run file.

    esm_runscripts generates files with pattern:
    {expid}_{cluster}_{datestamp}.run

    Parameters
    ----------
    expid : str
        Experiment ID
    task : str
        Task name (prepcompute/compute/tidy/post)
    base_dir : Path, optional
        Base directory to search (default: current directory)

    Returns
    -------
    Path
        Path to the .run script

    Raises
    ------
    FileNotFoundError
        If run script cannot be found
    """
    search_dir = base_dir if base_dir else Path.cwd()

    # Search in common locations
    search_paths = [
        search_dir / expid / "scripts",
        search_dir / "scripts",
        search_dir,
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Pattern: {expid}_*.run
        # Find the most recent one matching the pattern
        pattern = f"{expid}_*.run"
        matches = list(search_path.glob(pattern))

        if matches:
            # Return the most recent one
            most_recent = max(matches, key=lambda p: p.stat().st_mtime)
            return most_recent

    raise FileNotFoundError(
        f"Could not find .run script for expid={expid} in {search_dir}"
    )


def extract_executable_content(run_script_path: Path) -> str:
    """
    Parse .run script and extract executable content.

    This function strips SLURM directives and sbatch commands while keeping
    all executable content including:
    - Shebang
    - Module load commands
    - Export statements
    - Working directory changes
    - Model execution commands

    Parameters
    ----------
    run_script_path : Path
        Path to the .run script

    Returns
    -------
    str
        Executable shell script content as string
    """
    with open(run_script_path) as f:
        lines = f.readlines()

    executable_lines = []
    skip_patterns = [
        r"^\s*#SBATCH",  # SLURM directives
        r"^\s*#\$",  # SGE/PBS directives (just in case)
        r".*sbatch\s+.*\.run",  # sbatch submission commands
    ]

    for line in lines:
        # Check if line should be skipped
        should_skip = any(re.match(pattern, line) for pattern in skip_patterns)

        if not should_skip:
            executable_lines.append(line)

    content = "".join(executable_lines)

    # Ensure we have content
    if not content.strip():
        raise ValueError(f"No executable content found in {run_script_path}")

    return content


def write_executable_script(content: str, output_path: Path):
    """
    Write executable content to a temporary script file.

    Parameters
    ----------
    content : str
        Shell script content
    output_path : Path
        Path where script should be written
    """
    with open(output_path, "w") as f:
        f.write(content)

    # Make executable
    os.chmod(output_path, 0o755)
