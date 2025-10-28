# Snakemake Wrappers for ESM-Tools

[Snakemake](https://snakemake.readthedocs.io) wrappers for managing Earth System Models using [esm-tools](https://github.com/esm-tools/esm_tools). This repository provides two complementary wrappers:

1. **esm_master**: Model installation (download, configure, compile)
2. **esm_runscripts**: Model execution (prepare, run, tidy, post-process)

## Quick Links

- [esm_master Documentation](esm_master/) - Model installation wrapper
- [esm_runscripts Documentation](esm_runscripts/) - Model execution wrapper
- [esm-tools GitHub](https://github.com/esm-tools/esm_tools)
- [esm-tools Documentation](https://esm-tools.readthedocs.io)

## Overview

### esm_master Wrapper

This wrapper executes `esm_master` subcommands for installing Earth System Models. It supports all esm_master operations:

- **get**: Downloads model source code from repositories
- **conf**: Configures the model for compilation
- **comp**: Compiles the model binaries
- **clean**: Cleans build artifacts
- **install**: Complete installation (get + conf + comp)
- **recomp**: Reconfigures and recompiles the model

All subcommands follow the pattern: `esm_master <subcommand>-<model>-<version>`

### esm_runscripts Wrapper

This wrapper executes `esm_runscripts` phases for running Earth System Model simulations. It supports all simulation phases:

- **prepcompute**: Prepares files and environment before computation
- **compute**: Executes the coupled model simulation
- **tidy**: Post-run cleanup and file management
- **post**: Post-processing and data analysis

The wrapper uses a sophisticated two-stage approach:
1. **Resource extraction**: Automatically determines SLURM resource requirements
2. **Execution**: Runs simulation phases within Snakemake's resource management

See the [esm_runscripts README](esm_runscripts/README.md) for detailed documentation.

## Complete Workflow Example

Here's how both wrappers work together:

```python
from esm_runscripts_wrapper import get_resources

# 1. Install the model (esm_master)
rule install_model:
    output: touch("models/awicm-3.0/.installed")
    params:
        model="awicm",
        version="3.0"
    wrapper: "file://esm_master"

# 2. Run the simulation (esm_runscripts)
rule run_simulation:
    input: "models/awicm-3.0/.installed"
    output: touch("results/exp001_complete.done")
    params:
        runscript="awicm.yaml",
        task="compute",
        expid="exp001"
    resources:
        **get_resources("awicm.yaml", "compute", expid="exp001")
    wrapper: "file://esm_runscripts"
```

---

## esm_master Usage

### Installation (Default)

```python
rule install_model:
    output:
        touch("models/awicm-3.0/.installed")
    params:
        model="awicm",
        version="3.0",
        # subcommand="install"  # Optional: defaults to "install"
    log:
        "logs/esm_master/awicm-3.0-install.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"
```

### Download Only (get)

```python
rule download_model:
    output:
        touch("models/fesom-2.0/.downloaded")
    params:
        subcommand="get",
        model="fesom",
        version="2.0",
    log:
        "logs/esm_master/fesom-2.0-get.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"
```

### Configure Model (conf)

```python
rule configure_model:
    output:
        touch("models/echam-6.3/.configured")
    params:
        subcommand="conf",
        model="echam",
        version="6.3",
    log:
        "logs/esm_master/echam-6.3-conf.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"
```

### Compile Model (comp)

```python
rule compile_model:
    output:
        touch("models/echam-6.3/.compiled")
    params:
        subcommand="comp",
        model="echam",
        version="6.3",
    log:
        "logs/esm_master/echam-6.3-comp.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"
```

### Recompile Model (recomp)

```python
rule recompile_model:
    output:
        touch("models/awicm-3.0/.recompiled")
    params:
        subcommand="recomp",
        model="awicm",
        version="3.0",
    log:
        "logs/esm_master/awicm-3.0-recomp.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"
```

### Clean Build Artifacts (clean)

```python
rule clean_model:
    output:
        touch("models/fesom-2.0/.cleaned")
    params:
        subcommand="clean",
        model="fesom",
        version="2.0",
    log:
        "logs/esm_master/fesom-2.0-clean.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"
```

### With Additional Options

```python
rule install_model_verbose:
    output:
        touch("models/tux-1.0/.installed")
    params:
        subcommand="install",
        model="tux",
        version="1.0",
        extra="--verbose --check"  # Pass additional esm-master flags
    log:
        "logs/esm_master/tux-1.0-install.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"
```

### Testing Locally

To test the wrapper locally before publishing, use the `file://` protocol:

```python
rule install_test_model:
    output:
        touch("models/tux-1.0/.installed")
    params:
        model="tux",
        version="1.0",
    log:
        "logs/esm_master/tux-1.0.log"
    wrapper:
        "file:///path/to/snakemake-wrapper-esm-master"
```

Then run:
```bash
# Test the wrapper
snakemake -s your_snakefile.smk --use-conda -c1

# Or cd to the test directory
cd test/
snakemake --use-conda -c1
```

## Parameters

### Required Parameters

- **model** (str): Name of the Earth System Model (e.g., "awicm", "fesom", "tux")
- **version** (str): Version of the model (e.g., "3.0", "2.0", "1.0")

### Optional Parameters

- **subcommand** (str): ESM-Master operation to perform. Options: "get", "conf", "comp", "clean", "install", "recomp" (default: "install")
- **extra** (str): Additional command-line arguments to pass to `esm_master` (e.g., "--verbose", "--check", "--ignore-errors")

## Output

The wrapper doesn't produce specific output files by design, as `esm_master` operates on models in its configured directory structure. Use `touch()` to create marker files indicating successful operations:

```python
# Installation
output: touch("models/{model}-{version}/.installed")

# Download
output: touch("models/{model}-{version}/.downloaded")

# Configuration
output: touch("models/{model}-{version}/.configured")

# Compilation
output: touch("models/{model}-{version}/.compiled")
```

## Log Files

All stdout and stderr from the `esm_master` command are captured in the specified log file:

```python
log:
    "logs/esm_master/{model}-{version}.log"
```

## Requirements

### Dependencies

- **esm-tools** v6.59.2 (installed from git via pip)
- **Python** >= 3.8

The wrapper automatically creates a conda environment with these dependencies.

### ESM-Tools Configuration

The wrapper requires a properly configured esm-tools environment. Ensure that:
- You have access to the required model repositories
- Authentication credentials are set up (for private repositories)
- The target compute environment is supported by esm-tools

### Git Authentication (Critical for Private Repositories)

**⚠️ Important**: Snakemake cannot handle interactive authentication prompts. If your workflow hangs or fails during the `get` subcommand, it's likely waiting for git credentials.

This wrapper executes `esm_master` commands in a non-interactive environment. For workflows involving private git repositories, you **must** configure password-less git authentication before running Snakemake.

#### Recommended Solutions

**ESM-Tools uses HTTPS URLs for git repositories**, so you need to configure credential storage for HTTPS authentication.

**Option 1: Git Credential Helper (Recommended for HTTPS)**
```bash
# Cache credentials in memory for 1 hour (safest for shared systems)
git config --global credential.helper 'cache --timeout=3600'

# Or store credentials persistently in system keychain (more convenient)
git config --global credential.helper osxkeychain  # macOS
git config --global credential.helper libsecret    # Linux
git config --global credential.helper manager      # Windows

# After setting credential helper, authenticate once:
git ls-remote https://github.com/esm-tools/esm_tools.git
# Enter credentials when prompted - they'll be cached/stored
```

**Option 2: Personal Access Token in Git Config**
```bash
# For GitHub - use gh CLI (recommended)
gh auth login
# Follow prompts and choose HTTPS protocol

# For GitLab - use glab CLI (recommended)
glab auth login
# Follow prompts and choose HTTPS protocol

# Alternatively, for GitLab - store token in git credential store
git config --global credential.helper store
echo "https://oauth2:YOUR_GITLAB_TOKEN@gitlab.com" >> ~/.git-credentials

# For general use - embed token in git config (less secure)
git config --global url."https://YOUR_TOKEN@github.com/".insteadOf "https://github.com/"
```

**Option 3: Environment Variables**
```bash
# Some tools respect these environment variables
export GIT_ASKPASS=echo
export GH_TOKEN="ghp_your_github_token"
export GITLAB_TOKEN="glpat_your_gitlab_token"

# Run Snakemake with these variables set
snakemake --use-conda -c1
```

**Option 4: Pre-authenticate (Simplest for Testing)**
```bash
# Manually run get step first to trigger authentication
esm_master get-awicm-3.0
# Enter credentials when prompted

# If using credential.helper cache/store, credentials are now cached
# Then run your Snakemake workflow
snakemake --use-conda -c1
```

#### Testing Authentication

Before running your Snakemake workflow, verify password-less HTTPS git access:
```bash
# Test HTTPS authentication (should not prompt for credentials)
git ls-remote https://github.com/esm-tools/esm_tools.git

# Or test a manual clone
git clone https://github.com/esm-tools/esm_tools.git /tmp/test-clone
rm -rf /tmp/test-clone

# If prompted for credentials, your credential helper is not configured correctly
```

#### Troubleshooting

If your workflow hangs indefinitely:
1. Check if `esm_master` is waiting for credentials: `ps aux | grep esm_master`
2. Kill the Snakemake process: `Ctrl+C`
3. Set up password-less authentication using one of the options above
4. Re-run your workflow

**Note**: Setting up password-less git authentication is technically out of scope for this wrapper, but is essential for automated workflows. Consult your organization's git documentation or the [GitHub SSH documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) for detailed setup instructions.

## Available Models

Common models supported by esm-tools include:
- **awicm** - AWI Climate Model
- **fesom** - Finite Element Sea Ice-Ocean Model
- **echam** - ECHAM atmospheric model
- **tux** - Test model (downloads a simple file via curl)

For a complete list of available models and versions, consult the [esm-tools documentation](https://esm-tools.readthedocs.io) or run:
```bash
esm_master --list_all_targets
```

## Example Workflow

Here's a complete example workflow demonstrating different subcommands:

```python
MODELS = {
    "tux": "1.0",
    "awicm": "3.0",
    "fesom": "2.0"
}

rule all:
    input:
        expand("models/{model}-{version}/.installed",
               zip,
               model=MODELS.keys(),
               version=MODELS.values())

# Full installation (get + conf + comp)
rule install_model:
    output:
        touch("models/{model}-{version}/.installed")
    params:
        model="{model}",
        version="{version}",
        # subcommand defaults to "install"
    log:
        "logs/esm_master/{model}-{version}-install.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"

# Multi-stage installation with separate steps
rule download_model:
    output:
        touch("models/{model}-{version}/.downloaded")
    params:
        subcommand="get",
        model="{model}",
        version="{version}",
    log:
        "logs/esm_master/{model}-{version}-get.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"

rule configure_model:
    input:
        "models/{model}-{version}/.downloaded"
    output:
        touch("models/{model}-{version}/.configured")
    params:
        subcommand="conf",
        model="{model}",
        version="{version}",
    log:
        "logs/esm_master/{model}-{version}-conf.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"

rule compile_model:
    input:
        "models/{model}-{version}/.configured"
    output:
        touch("models/{model}-{version}/.compiled")
    params:
        subcommand="comp",
        model="{model}",
        version="{version}",
    log:
        "logs/esm_master/{model}-{version}-comp.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/main/esm_master_install"
```

## Notes

- The `install` subcommand performs a complete installation (get + conf + comp)
- You can break installation into stages using separate `get`, `conf`, and `comp` rules
- The `recomp` subcommand reconfigures and recompiles without re-downloading
- Installation locations are determined by esm-tools configuration
- For large models, compilation may take significant time and resources
- Use the `tux-1.0` test model for quick validation of the wrapper
- The `subcommand` parameter defaults to "install" for backward compatibility

## License

MIT License

## Author

Paul Gierz (paul.gierz@awi.de)

## Links

- [esm-tools GitHub](https://github.com/esm-tools/esm_tools)
- [esm-tools Documentation](https://esm-tools.readthedocs.io)
- [Snakemake Wrappers](https://snakemake-wrappers.readthedocs.io)
