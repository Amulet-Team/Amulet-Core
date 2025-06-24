cmake_minimum_required(VERSION 3.13)

project(amulet_core LANGUAGES CXX)

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

if (MSVC)
    add_definitions("/MP")
endif()

# Find libraries
find_package(pybind11 CONFIG REQUIRED)
find_package(amulet_pybind11_extensions CONFIG REQUIRED)
find_package(amulet_io CONFIG REQUIRED)
find_package(amulet_nbt CONFIG REQUIRED)

# Find C++ files
file(REAL_PATH src SOURCE_PATH)
file(GLOB_RECURSE EXTENSION_SOURCES LIST_DIRECTORIES false ${SOURCE_PATH}/amulet/*.py.cpp)
file(GLOB_RECURSE EXTENSION_HEADERS LIST_DIRECTORIES false ${SOURCE_PATH}/amulet/*.py.hpp)
file(GLOB_RECURSE SOURCES LIST_DIRECTORIES false ${SOURCE_PATH}/amulet/*.cpp)
file(GLOB_RECURSE HEADERS LIST_DIRECTORIES false ${SOURCE_PATH}/amulet/*.hpp)
list(REMOVE_ITEM SOURCES ${EXTENSION_SOURCES})
list(REMOVE_ITEM HEADERS ${EXTENSION_HEADERS})

# Add implementation
add_library(amulet_core SHARED)
target_compile_definitions(amulet_core PRIVATE ExportAmuletCore)
target_link_libraries(amulet_core PUBLIC amulet_io)
target_link_libraries(amulet_core PUBLIC amulet_nbt)
target_include_directories(amulet_core PUBLIC ${SOURCE_PATH})
target_sources(amulet_core PRIVATE ${SOURCES} ${HEADERS})
foreach(FILE ${SOURCES} ${HEADERS})
    file(RELATIVE_PATH REL_PATH ${SOURCE_PATH} ${FILE})
    get_filename_component(GROUP ${REL_PATH} DIRECTORY)
    string(REPLACE "/" "\\" GROUP ${GROUP})
    source_group(${GROUP} FILES ${FILE})
endforeach()

# Add python extension
pybind11_add_module(_amulet_core)
target_link_libraries(_amulet_core PRIVATE amulet_pybind11_extensions)
target_link_libraries(_amulet_core PRIVATE amulet_core)
target_compile_definitions(_amulet_core PRIVATE PYBIND11_DETAILED_ERROR_MESSAGES)
target_compile_definitions(_amulet_core PRIVATE PYBIND11_VERSION="${pybind11_VERSION}")
target_compile_definitions(_amulet_core PRIVATE COMPILER_ID="${CMAKE_CXX_COMPILER_ID}")
target_compile_definitions(_amulet_core PRIVATE COMPILER_VERSION="${CMAKE_CXX_COMPILER_VERSION}")
target_sources(_amulet_core PRIVATE ${EXTENSION_SOURCES} ${EXTENSION_HEADERS})
foreach(FILE ${EXTENSION_SOURCES} ${EXTENSION_HEADERS})
    file(RELATIVE_PATH REL_PATH ${SOURCE_PATH} ${FILE})
    get_filename_component(GROUP ${REL_PATH} DIRECTORY)
    string(REPLACE "/" "\\" GROUP ${GROUP})
    source_group(${GROUP} FILES ${FILE})
endforeach()

if(NOT DEFINED AMULET_CORE_EXT_DIR)
    set(AMULET_CORE_EXT_DIR ${amulet_core_DIR})
endif()

# Install
install(TARGETS amulet_core DESTINATION ${amulet_core_DIR})
install(TARGETS _amulet_core DESTINATION ${AMULET_CORE_EXT_DIR})

if (DEFINED BUILD_AMULET_CORE_TESTS)
    add_subdirectory(tests)
endif()
