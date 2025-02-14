import sys
from setuptools import setup, Extension
from torch.utils.cpp_extension import BuildExtension, include_paths, library_paths

# Collecting include and library paths
include_dirs = include_paths()
library_dirs = library_paths()
libraries = ["c10", "torch", "torch_cpu"]

extra_compile_args = ["-std=c++17"]
extra_link_args = []
if sys.platform == "darwin":
    shared_lib_ext = ".dylib"
    extra_compile_args.append("-stdlib=libc++")
    extra_link_args.extend(["-stdlib=libc++", "-mmacosx-version-min=10.9"])
elif sys.platform == "linux":
    extra_compile_args.append("-fPIC")
    shared_lib_ext = ".so"
else:
    raise RuntimeError(f"Unsupported platform {sys.platform}")


# Define the extension
neighbors_convert_extension = Extension(
    name="pet_neighbors_convert.neighbors_convert",
    sources=["src/pet_neighbors_convert/neighbors_convert.cpp"],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries,
    language="c++",
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

setup(
    ext_modules=[neighbors_convert_extension],
    cmdclass={"build_ext": BuildExtension.with_options(no_python_abi_suffix=True)},
    package_data={"pet_neighbors_convert": [f"neighbors_convert{shared_lib_ext}"]},
)
