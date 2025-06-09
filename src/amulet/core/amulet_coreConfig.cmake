if (NOT TARGET amulet_core)
    message(STATUS "Finding amulet_core")

    find_package(amulet_io CONFIG REQUIRED)
    find_package(amulet_nbt CONFIG REQUIRED)

    set(amulet_core_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")
    find_library(amulet_core_LIBRARY NAMES amulet_core PATHS "${CMAKE_CURRENT_LIST_DIR}")
    message(STATUS "amulet_core_LIBRARY: ${amulet_core_LIBRARY}")

    add_library(amulet_core_bin SHARED IMPORTED)
    set_target_properties(amulet_core_bin PROPERTIES
        IMPORTED_IMPLIB "${amulet_core_LIBRARY}"
    )

    add_library(amulet_core INTERFACE)
    target_link_libraries(amulet_core INTERFACE amulet_io)
    target_link_libraries(amulet_core INTERFACE amulet_nbt)
    target_link_libraries(amulet_core INTERFACE amulet_core_bin)
    target_include_directories(amulet_core INTERFACE ${amulet_core_INCLUDE_DIR})
endif()
