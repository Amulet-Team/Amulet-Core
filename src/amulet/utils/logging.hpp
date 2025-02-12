#pragma once

#include <string>

#include <amulet/dll.hpp>
#include <amulet/utils/signal.hpp>

namespace Amulet {

AMULET_CORE_EXPORT void unregister_default_log_handler();

AMULET_CORE_EXPORT extern Signal<int, std::string> logger;

AMULET_CORE_EXPORT void log(int level, const std::string& msg);

AMULET_CORE_EXPORT void debug(const std::string& msg);
AMULET_CORE_EXPORT void info(const std::string& msg);
AMULET_CORE_EXPORT void warning(const std::string& msg);
AMULET_CORE_EXPORT void error(const std::string& msg);
AMULET_CORE_EXPORT void critical(const std::string& msg);

}
