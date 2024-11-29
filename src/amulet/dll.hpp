#ifndef AMULET_CORE_DLLX
    #ifdef _WIN32
        #ifdef ExportAmuletCore
            #define AMULET_CORE_DLLX __declspec(dllexport)
        #else
            #define AMULET_CORE_DLLX __declspec(dllimport)
        #endif
    #else
        #define AMULET_CORE_DLLX
    #endif
#endif
