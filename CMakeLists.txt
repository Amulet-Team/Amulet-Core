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

# Add zlib
set(ZLIB_BUILD_EXAMPLES OFF)
add_subdirectory(submodules/zlib)
set(ZLIB_ROOT submodules/zlib)
set(ZLIB_USE_STATIC_LIBS ON)
set(ZLIB_LIBRARY ${INSTALL_LIB_DIR})
find_package(ZLIB REQUIRED)

# Add pybind11
find_package(pybind11 CONFIG REQUIRED)
find_package(pybind11_extensions CONFIG REQUIRED)

# Add Amulet NBT
find_package(amulet_nbt CONFIG REQUIRED)
find_package(leveldb_mcpe CONFIG REQUIRED)

# Find C++ files
file(GLOB_RECURSE AMULET_EXTENSION_SOURCES LIST_DIRECTORIES false src/amulet/*.py.cpp)
file(GLOB_RECURSE AMULET_SOURCES LIST_DIRECTORIES false src/amulet/*.cpp)
list(REMOVE_ITEM AMULET_SOURCES ${AMULET_EXTENSION_SOURCES})

# Add implementation
add_library(amulet_core SHARED)
target_link_libraries( amulet_core PRIVATE zlibstatic )
target_link_libraries( amulet_core PRIVATE amulet_nbt )
target_link_libraries( amulet_core PRIVATE leveldb_mcpe )
target_compile_definitions(amulet_core PRIVATE ExportAmuletCore)
target_include_directories(amulet_core PUBLIC src)
target_sources(amulet_core PRIVATE ${AMULET_SOURCES})

# Add python extension
pybind11_add_module(_amulet)
target_link_libraries( _amulet PRIVATE amulet_nbt )
target_link_libraries( _amulet PRIVATE leveldb_mcpe )
target_link_libraries( _amulet PRIVATE amulet_core )
target_link_libraries( _amulet PRIVATE pybind11_extensions )
target_compile_definitions(_amulet PRIVATE PYBIND11_DETAILED_ERROR_MESSAGES)
target_compile_definitions(_amulet PRIVATE PYBIND11_VERSION="${pybind11_VERSION}")
target_compile_definitions(_amulet PRIVATE COMPILER_ID="${CMAKE_CXX_COMPILER_ID}")
target_compile_definitions(_amulet PRIVATE COMPILER_VERSION="${CMAKE_CXX_COMPILER_VERSION}")
target_sources(_amulet PRIVATE ${AMULET_EXTENSION_SOURCES})

# Install
install(TARGETS amulet_core DESTINATION "${SRC_INSTALL_DIR}/amulet")
install(TARGETS _amulet DESTINATION "${SRC_INSTALL_DIR}/amulet")
