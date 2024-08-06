# version 0.5.0

import sys
import json
import textwrap
import subprocess

help_message = """
Usage: python conda_export.py -p environment_path
       python conda_export.py -n environment_name

This script export a given environment with the following constraints:

- only list the conda packages installed directly using the environment history,
- pin the version of these packages,
- also export pip installed packages with their version,
- remove `defaults` channel,
- add `conda-forge` channel,
- do not export the prefix or name of the environment.
"""

if len(sys.argv) != 3 or sys.argv[1] not in ["-p", "-n"]:
    print(help_message.strip())
    sys.exit(1)

env_flag = sys.argv[1]
env_location = sys.argv[2]

definition_full = subprocess.check_output(
    ["conda", "env", "export", env_flag, env_location, "--no-builds", "--json"]
)
definition_full = json.loads(definition_full)

definition_history = subprocess.check_output(
    ["conda", "env", "export", env_flag, env_location, "--from-history", "--json"]
)
definition_history = json.loads(definition_history)

# find pip packages and conda packages versions from the full definition
pkg_versions = {}
pip_pkgs = None
for pkg in definition_full["dependencies"]:
    if isinstance(pkg, dict) and "pip" in pkg:
        pip_pkgs = pkg["pip"]
        continue

    pkg_name, pkg_version = pkg.split("=", maxsplit=1)
    pkg_versions[pkg_name] = pkg_version

# inject pip packages and version in the historical definition
dependencies = []

for pkg in definition_history["dependencies"]:
    if "=" in pkg:
        dependencies.append(pkg)
        continue

    # handle case of package with a channel name
    pkg_name = pkg.split("::", maxsplit=1)[1] if "::" in pkg else pkg

    if pkg_name not in pkg_versions:
        print(
            f"WARNING: Conda package '{pkg}' listed in environment installation "
            "history but not present in current environment. It will be removed "
            "from the environment definition.",
            file=sys.stderr,
        )
        continue

    dependencies.append(f"{pkg}={pkg_versions[pkg_name]}")

if pip_pkgs is not None:
    dependencies.append({"pip": pip_pkgs})

definition_history["dependencies"] = dependencies

# remove defaults channel and add conda-forge
channels = [chan for chan in definition_history["channels"] if chan != "defaults"]
if "conda-forge" not in channels:
    channels.append("conda-forge")
definition_history["channels"] = channels

# remove any prefix or name to force user to set them
del definition_history["prefix"]
del definition_history["name"]


# export to yaml by-hand (to avoid dependency on 3rd party package)
def to_yaml(obj):
    if isinstance(obj, list):
        lines = []
        for elem in obj:
            txt = "-" + textwrap.indent(to_yaml(elem), "  ")[1:]
            lines.append(txt)
        return "\n".join(lines)
    elif isinstance(obj, dict):
        lines = []
        for key, elem in obj.items():
            txt = textwrap.indent(to_yaml(elem), "  ")
            lines.append(f"{key}:\n{txt}")
        return "\n".join(lines)
    else:
        return str(obj)


print(to_yaml(definition_history))
