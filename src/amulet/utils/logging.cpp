#include <mutex>
#include <string>

#include "logging.hpp"

namespace Amulet {

static std::mutex log_mutex;

static int log_level = 20;

static void default_log_handler(int level, const std::string& msg)
{
    if (log_level <= level) {
        std::unique_lock lock(log_mutex);
        std::cout << msg << std::endl;
    }
}

Amulet::Signal<int, std::string> logger;
static Amulet::SignalToken<int, std::string> default_log_handler_token = logger.connect(&default_log_handler);

void register_default_log_handler()
{
    default_log_handler_token = logger.connect(default_log_handler);
}

void unregister_default_log_handler() {
    logger.disconnect(default_log_handler_token);
}

int get_default_log_level() {
    return log_level;
}

void set_default_log_level(int level) {
    log_level = level;
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
