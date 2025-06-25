cmake_minimum_required(VERSION 3.13)

project(get_compiler LANGUAGES CXX)

# Set C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

write_file("${CMAKE_BINARY_DIR}/compiler_id.txt" "${CMAKE_CXX_COMPILER_ID}")
write_file("${CMAKE_BINARY_DIR}/compiler_version.txt" "${CMAKE_CXX_COMPILER_VERSION}")
