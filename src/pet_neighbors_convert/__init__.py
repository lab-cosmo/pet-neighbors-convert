import os
import sys
from collections import namedtuple

import torch

import re
import glob

from ._version import __version__  # noqa


_Version = namedtuple("Version", ["major", "minor", "patch"])


def _parse_version(version):
    match = re.match(r"(\d+)\.(\d+)\.(\d+).*", version)
    if match:
        return _Version(*map(int, match.groups()))
    else:
        raise ValueError("Invalid version string format")


_HERE = os.path.realpath(os.path.dirname(__file__))


def _lib_path():
    torch_version = _parse_version(torch.__version__)
    expected_prefix = os.path.join(
        _HERE, f"torch-{torch_version.major}.{torch_version.minor}"
    )
    if os.path.exists(expected_prefix):
        if sys.platform.startswith("darwin"):
            path = os.path.join(expected_prefix, "lib", "libneighbors_convert.dylib")
        elif sys.platform.startswith("linux"):
            path = os.path.join(expected_prefix, "lib", "libneighbors_convert.so")
        elif sys.platform.startswith("win"):
            path = os.path.join(expected_prefix, "bin", "neighbors_convert.dll")
        else:
            raise ImportError("Unknown platform. Please edit this file")

        if os.path.isfile(path):
            return path
        else:
            raise ImportError(
                "Could not find neighbors_convert shared library at " + path
            )

    # gather which torch version(s) the current install was built
    # with to create the error message
    existing_versions = []
    for prefix in glob.glob(os.path.join(_HERE, "torch-*")):
        existing_versions.append(os.path.basename(prefix)[11:])

    if len(existing_versions) == 1:
        raise ImportError(
            f"Trying to load neighbors-convert with torch v{torch.__version__}, "
            f"but it was compiled against torch v{existing_versions[0]}, which "
            "is not ABI compatible"
        )
    else:
        all_versions = ", ".join(map(lambda version: f"v{version}", existing_versions))
        raise ImportError(
            f"Trying to load neighbors-convert with torch v{torch.__version__}, "
            f"we found builds for torch {all_versions}; which are not ABI compatible.\n"
            "You can try to re-install from source with "
            "`pip install neighbors-convert --no-binary=neighbors-convert`"
        )


# load the C++ operators and custom classes
torch.classes.load_library(_lib_path())
