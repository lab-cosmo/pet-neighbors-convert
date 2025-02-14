cmake_minimum_required(VERSION 3.27)

if (POLICY CMP0076)
    #  target_sources() converts relative paths to absolute
    cmake_policy(SET CMP0076 NEW)
endif()

project(neighbors_convert CXX)

# Set a default build type if none was specified
if (${CMAKE_CURRENT_SOURCE_DIR} STREQUAL ${CMAKE_SOURCE_DIR})
    if("${CMAKE_BUILD_TYPE}" STREQUAL "" AND "${CMAKE_CONFIGURATION_TYPES}" STREQUAL "")
        message(STATUS "Setting build type to 'relwithdebinfo' as none was specified.")
        set(
            CMAKE_BUILD_TYPE "relwithdebinfo"
            CACHE STRING
            "Choose the type of build, options are: none(CMAKE_CXX_FLAGS or CMAKE_C_FLAGS used) debug release relwithdebinfo minsizerel."
            FORCE
        )
        set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS release debug relwithdebinfo minsizerel none)
    endif()
endif()

# add path to the cmake configuration of the version of libtorch used
# by the Python torch module. PYTHON_EXECUTABLE is provided by skbuild
execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -c "import torch.utils; print(torch.utils.cmake_prefix_path)"
    RESULT_VARIABLE TORCH_CMAKE_PATH_RESULT
    OUTPUT_VARIABLE TORCH_CMAKE_PATH_OUTPUT
    ERROR_VARIABLE TORCH_CMAKE_PATH_ERROR
)

if (NOT ${TORCH_CMAKE_PATH_RESULT} EQUAL 0)
message(FATAL_ERROR "failed to find your pytorch installation\n${TORCH_CMAKE_PATH_ERROR}")
endif()

string(STRIP ${TORCH_CMAKE_PATH_OUTPUT} TORCH_CMAKE_PATH_OUTPUT)
set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH};${TORCH_CMAKE_PATH_OUTPUT}")

find_package(Torch 2.3 REQUIRED)

file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/_build_torch_version.py "BUILD_TORCH_VERSION = '${Torch_VERSION}'")

add_library(neighbors_convert SHARED 
    "src/pet_neighbors_convert/neighbors_convert.cpp"
)

# only link to `torch_cpu_library` instead of `torch`, which could also include
# `libtorch_cuda`.
target_link_libraries(neighbors_convert PUBLIC torch_cpu_library)
target_include_directories(neighbors_convert PUBLIC "${TORCH_INCLUDE_DIRS}")
target_compile_definitions(neighbors_convert PUBLIC "${TORCH_CXX_FLAGS}")

target_compile_features(neighbors_convert PUBLIC cxx_std_17)

install(TARGETS neighbors_convert
    LIBRARY DESTINATION "lib"
)
