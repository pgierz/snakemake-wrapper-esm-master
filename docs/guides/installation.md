# Installation

This guide covers how to set up and use the ESM-Tools Snakemake wrappers in your projects.

## Prerequisites

### Required Software

- **Python** >= 3.8
- **Snakemake** >= 7.0
- **Conda** or **Mamba** (for environment management)
- **Git** (for repository access)

### ESM-Tools Access

Ensure you have access to:
- ESM-Tools repositories (public or private)
- Model source code repositories
- Compute resources where models will run

## Wrapper Installation

The wrappers don't require installation themselves - they're used directly in your Snakemake workflows via the `wrapper:` directive.

### Using Published Wrappers

Reference wrappers directly from GitHub:

```python
# esm_master wrapper
wrapper: "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"

# esm_runscripts wrapper
wrapper: "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_runscripts"
```

### Using Local Development Versions

For testing or development:

```python
# Clone the repository
git clone https://github.com/pgierz/snakemake-wrapper-esm-master.git

# Reference local wrappers in your Snakefile
wrapper: "file:///path/to/snakemake-wrapper-esm-master/esm_master"
wrapper: "file:///path/to/snakemake-wrapper-esm-master/esm_runscripts"
```

## Environment Setup

The wrappers automatically create conda environments with required dependencies:

### esm_master Dependencies

- Python 3.10
- esm-tools v6.59.2
- Git and build tools

### esm_runscripts Dependencies

- Python 3.10
- esm-tools v6.59.2
- **herrkunft** (YAML provenance tracking library)

## Git Authentication

```{important}
For private repositories, configure password-less git authentication **before** running Snakemake workflows.
```

### Option 1: Git Credential Helper (Recommended)

```bash
# Cache credentials in memory for 1 hour
git config --global credential.helper 'cache --timeout=3600'

# Or use system keychain
git config --global credential.helper osxkeychain  # macOS
git config --global credential.helper libsecret    # Linux
git config --global credential.helper manager      # Windows

# Authenticate once
git ls-remote https://github.com/esm-tools/esm_tools.git
```

### Option 2: Personal Access Token

```bash
# GitHub
gh auth login

# GitLab
glab auth login

# Or manually
git config --global url."https://YOUR_TOKEN@github.com/".insteadOf "https://github.com/"
```

### Option 3: SSH Keys

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub/GitLab account
cat ~/.ssh/id_ed25519.pub
```

### Testing Authentication

```bash
# Should NOT prompt for password
git ls-remote https://github.com/esm-tools/esm_tools.git

# Test SSH (if using SSH)
ssh -T git@github.com
```

## Verifying Installation

Create a test Snakefile:

```python
# test.smk
rule test_esm_master:
    output:
        touch("test/.installed")
    params:
        model="tux",
        version="1.0",
    log:
        "log/test.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

Run the test:

```bash
snakemake -s test.smk --use-conda -c1
```

If successful, you'll see:
- Conda environment created
- esm_master downloading tux model
- Output file `.installed` created

## Troubleshooting

### Wrapper Cannot Be Found

```
Error: wrapper directive could not be resolved
```

**Solution:** Check your internet connection and verify the GitHub URL is correct.

### Git Authentication Timeout

```
(hanging during 'get' subcommand)
```

**Solution:** Configure password-less git authentication (see above).

### Conda Environment Issues

```
CondaError: Unable to create environment
```

**Solution:**
```bash
# Clear conda cache
conda clean --all

# Try with mamba instead
snakemake --use-conda --conda-frontend mamba
```

### Module Not Found Errors

```
ModuleNotFoundError: No module named 'herrkunft'
```

**Solution:** The wrapper will install it automatically. If issues persist:
```bash
# Verify pip is available in conda environment
conda activate snakemake
pip install herrkunft
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [esm_master Usage](esm_master_usage.md)
- [esm_runscripts Usage](esm_runscripts_usage.md)
