cmake_minimum_required(VERSION 3.13)

project(pybind11_extensions LANGUAGES CXX)

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
find_package(pybind11 CONFIG REQUIRED)
find_package(pybind11_extensions CONFIG REQUIRED)
find_package(amulet_nbt CONFIG REQUIRED)
find_package(leveldb_mcpe CONFIG REQUIRED)
find_package(amulet_core CONFIG REQUIRED)

# Find sources
file(REAL_PATH test_amulet SOURCE_PATH)
file(GLOB_RECURSE TEST_AMULET_SOURCES LIST_DIRECTORIES false ${SOURCE_PATH}/*.py.cpp)

pybind11_add_module(_test_amulet)
target_compile_definitions(_test_amulet PRIVATE PYBIND11_DETAILED_ERROR_MESSAGES)
target_link_libraries(_test_amulet PRIVATE pybind11_extensions)
target_link_libraries(_test_amulet PRIVATE amulet_nbt)
target_link_libraries(_test_amulet PRIVATE leveldb_mcpe)
target_link_libraries(_test_amulet PRIVATE amulet_core)
target_sources(_test_amulet PRIVATE ${TEST_AMULET_SOURCES})
install(TARGETS _test_amulet DESTINATION ".")
