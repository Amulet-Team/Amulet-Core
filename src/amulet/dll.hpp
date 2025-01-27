#pragma once

#ifndef AMULET_CORE_DLLX
    #if defined(WIN32) || defined(_WIN32)
        #ifdef ExportAmuletCore
            #define AMULET_CORE_DLLX __declspec(dllexport)
        #else
            #define AMULET_CORE_DLLX __declspec(dllimport)
        #endif
    #else
        #define AMULET_CORE_DLLX
    #endif
#endif

#if !defined(AMULET_CORE_EXPORT_EXCEPTION)
    #if defined(_LIBCPP_EXCEPTION)
        #define AMULET_CORE_EXPORT_EXCEPTION __attribute__((visibility("default")))
    #else
        #define AMULET_CORE_EXPORT_EXCEPTION
    #endif
#endif
