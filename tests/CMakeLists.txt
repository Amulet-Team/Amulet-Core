cmake_minimum_required(VERSION 3.13)

project(amulet_core_tests LANGUAGES CXX)

# Set C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set platform variables
if (WIN32)
	# set windows 7 as the minimum version
	add_definitions(-D_WIN32_WINNT=0x0601)
elseif(APPLE)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15")
else()
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

# Find dependencies
if (NOT TARGET pybind11::module)
    find_package(pybind11 CONFIG REQUIRED)
endif()
if (NOT TARGET amulet_pybind11_extensions)
    find_package(amulet_pybind11_extensions CONFIG REQUIRED)
endif()
if (NOT TARGET amulet_test_utils)
    find_package(amulet_test_utils CONFIG REQUIRED)
endif()
if (NOT TARGET amulet_core)
    find_package(amulet_core CONFIG REQUIRED)
endif()

# Find sources
file(GLOB_RECURSE SOURCES LIST_DIRECTORIES false "${CMAKE_CURRENT_LIST_DIR}/*.py.cpp")

pybind11_add_module(_test_amulet_core)
target_compile_definitions(_test_amulet_core PRIVATE PYBIND11_DETAILED_ERROR_MESSAGES)
target_compile_definitions(_test_amulet_core PRIVATE PYBIND11_VERSION="${pybind11_VERSION}")
target_compile_definitions(_test_amulet_core PRIVATE COMPILER_ID="${CMAKE_CXX_COMPILER_ID}")
target_compile_definitions(_test_amulet_core PRIVATE COMPILER_VERSION="${CMAKE_CXX_COMPILER_VERSION}")
target_link_libraries(_test_amulet_core PRIVATE amulet_pybind11_extensions)
target_link_libraries(_test_amulet_core PRIVATE amulet_test_utils)
target_link_libraries(_test_amulet_core PRIVATE amulet_core)
target_sources(_test_amulet_core PRIVATE ${SOURCES})
foreach(FILE ${SOURCES})
    file(RELATIVE_PATH REL_PATH ${CMAKE_CURRENT_LIST_DIR} ${FILE})
    get_filename_component(GROUP ${REL_PATH} DIRECTORY)
    string(REPLACE "/" "\\" GROUP "${GROUP}")
    source_group(${GROUP} FILES ${FILE})
endforeach()

# Install
install(TARGETS _test_amulet_core DESTINATION "${CMAKE_CURRENT_LIST_DIR}/test_amulet_core")
