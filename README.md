# Conda environment exporter

This helper script export a conda environment specification, like`conda env export`, but with the following features:

- it only lists the conda packages installed directly using the environment history,
- it pins the version of these packages,
- it also exports pip-installed packages with their version,
- it removes the `defaults` channel,
- it adds `conda-forge` channel,
- it does not export the prefix or name of the environment.

The idea is to help recreate a conda environment *approximately* reproducible (pinning only the top level dependencies) and less painful to fix than a full export.

Example usage:

```
python conda_export.py -n my_cool_conda_environment
```

**Note:** Use `-n` to use the environment name or `-p` to use the environment path.

You can export the output to a yaml file and use it to create a new environment:

```
python conda_export.py -n my_cool_conda_environment > environment.yml
conda env create -f environment.yml -n my_cooler_conda_environment
```

**Note:** This script will crash with older versions of conda. It is know to work with version 23.10.0. 
