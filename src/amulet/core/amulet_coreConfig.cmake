if (NOT TARGET amulet_core)
    message(STATUS "Finding amulet_core")

    find_package(amulet_io CONFIG REQUIRED)
    find_package(amulet_nbt CONFIG REQUIRED)

    set(amulet_core_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")
    find_library(amulet_core_LIBRARY NAMES amulet_core PATHS "${CMAKE_CURRENT_LIST_DIR}")
    message(STATUS "amulet_core_LIBRARY: ${amulet_core_LIBRARY}")

    add_library(amulet_core SHARED IMPORTED)
    set_target_properties(amulet_core PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${amulet_core_INCLUDE_DIR}"
        INTERFACE_LINK_LIBRARIES amulet_io
        INTERFACE_LINK_LIBRARIES amulet_nbt
        IMPORTED_IMPLIB "${amulet_core_LIBRARY}"
    )
endif()
