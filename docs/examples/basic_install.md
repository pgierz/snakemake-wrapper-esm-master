# Example: Basic Model Installation

Simple example of installing a model with the esm_master wrapper.

## Snakefile

```python
rule install_tux:
    output:
        touch("models/tux-1.0/.installed")
    params:
        model="tux",
        version="1.0"
    log:
        "log/install_tux.log"
    wrapper:
        "https://github.com/pgierz/snakemake-wrapper-esm-master/raw/master/esm_master"
```

## Run

```bash
snakemake --use-conda -c1
```

## Expected Output

```
Building DAG of jobs...
Creating conda environment...
Downloading model source...
Configuring model...
Compiling model...
Success!
```
