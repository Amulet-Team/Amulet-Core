#include <mutex>
#include <string>

#include "logging.hpp"

namespace Amulet {

static std::mutex log_mutex;

void default_log_handler(int level, const std::string& msg)
{
    if (level >= 20) {
        std::unique_lock lock(log_mutex);
        std::cout << msg << std::endl;
    }
}

Amulet::Signal<int, std::string> logger;
static Amulet::SignalToken<int, std::string> default_log_handler_token = logger.connect(&default_log_handler);

void unregister_default_log_handler() {
    logger.disconnect(default_log_handler_token);
}

void log(int level, const std::string& msg)
{
    logger.emit(level, msg);
}

void debug(const std::string& msg)
{
    log(10, msg);
}

void info(const std::string& msg)
{
    log(20, msg);
}

void warning(const std::string& msg)
{
    log(30, msg);
}

void error(const std::string& msg)
{
    log(40, msg);
}

void critical(const std::string& msg)
{
    log(50, msg);
}

} // namespace Amulet
