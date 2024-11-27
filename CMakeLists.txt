cmake_minimum_required(VERSION 3.13)

project(amulet_core LANGUAGES CXX)
set(SRC_INSTALL_DIR "." CACHE PATH "The path to the src directory to install into.")

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

# Add pybind11
find_package(pybind11 CONFIG REQUIRED)
find_package(pybind11_extensions CONFIG REQUIRED)

# Add Amulet NBT
find_package(amulet_nbt CONFIG REQUIRED)
find_package(leveldb_mcpe CONFIG REQUIRED)

# Find C++ files
file(GLOB EXTENSION_SOURCES src/amulet/**/*.py.cpp)
file(GLOB SOURCES src/amulet/**/*.cpp)
list(REMOVE_ITEM SOURCES ${EXTENSION_SOURCES})

# Add implementation
add_library(amulet_core SHARED)
target_compile_definitions(amulet_core PRIVATE ExportAmuletCore)
target_include_directories(amulet_core PUBLIC src)
target_sources(amulet_core PRIVATE ${SOURCES})

# Add python extension
pybind11_add_module(_amulet)
target_compile_definitions(_amulet PRIVATE PYBIND11_DETAILED_ERROR_MESSAGES)
target_link_libraries( _amulet PRIVATE amulet_core )
target_link_libraries( _amulet PRIVATE pybind11_extensions )
target_sources(_amulet PRIVATE ${EXTENSION_SOURCES})

# Install
install(TARGETS amulet_core DESTINATION "${SRC_INSTALL_DIR}/amulet")
install(TARGETS _amulet DESTINATION "${SRC_INSTALL_DIR}/amulet")
