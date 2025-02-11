#include <cstdlib>

#include "signal.hpp"

namespace Amulet {

namespace detail {

    EventLoop::EventLoop()
        : _thread(&EventLoop::_event_loop, this)
    {
    }

    EventLoop::~EventLoop()
    {
        std::cout << "EventLoop::~EventLoop()" << std::endl;
        exit();
    }

    void EventLoop::exit() {
        std::cout << "EventLoop::exit()" << std::endl;
        {
            std::unique_lock lock(_mutex);
            if (_exit) {
                return;
            }
            _exit = true;
            _condition.notify_one();
        }
        _thread.join();
    }

    void EventLoop::_event_loop()
    {
        std::unique_lock lock(_mutex);
        while (!_exit) {
            if (_events.empty()) {
                // If there are no events to process, wait until more are added.
                _condition.wait(lock);
                // Re-check the exit condition.
                continue;
            }
            auto event = _events.front();
            _events.pop_front();
            lock.unlock();
            try {
                event();
            } catch (const std::exception& e) {
                std::cout << "Unhandled exception in event loop: " << e.what() << std::endl;
            } catch (...) {
                std::cout << "Unhandled exception in event loop." << std::endl;
            }
            lock.lock();
        }
    }

    void EventLoop::submit(std::function<void()> event)
    {
        std::unique_lock lock(_mutex);
        _events.push_back(event);
        _condition.notify_one();
    }

    EventLoop global_event_loop;
    int global_event_loop_atexit_registered = std::atexit([] { global_event_loop.exit(); });

} // namespace detail

} // namespace Amulet
