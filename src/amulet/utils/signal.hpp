#pragma once

#include <condition_variable>
#include <functional>
#include <iostream>
#include <list>
#include <mutex>
#include <thread>

#include <amulet/dll.hpp>

namespace Amulet {

AMULET_CORE_EXPORT void error(const std::string& msg);

enum class ConnectionMode {
    Direct, // Directly called by the emitter.
    Async, // Called asynchronously.
};

namespace detail {

    class EventLoop {
    private:
        std::mutex _mutex;
        std::condition_variable _condition;
        std::thread _thread;
        std::list<std::function<void()>> _events;
        bool _exit = false;

        void _event_loop();

    public:
        AMULET_CORE_EXPORT EventLoop();
        AMULET_CORE_EXPORT ~EventLoop();
        AMULET_CORE_EXPORT void submit(std::function<void()> event);
        AMULET_CORE_EXPORT void exit();
    };

    AMULET_CORE_EXPORT extern EventLoop global_event_loop;

    template <typename... Args>
    class SignalCallbackStorage {
    public:
        std::mutex mutex;
        std::function<void(Args...)> callback;
        ConnectionMode mode;
        bool disconnected = false;

        SignalCallbackStorage(
            std::function<void(Args...)> callback,
            ConnectionMode mode)
            : callback(std::move(callback))
            , mode(mode)
        {
        }
    };

} // namespace detail

template <typename... Args>
class Signal;

template <typename... Args>
class SignalToken {
private:
    std::shared_ptr<detail::SignalCallbackStorage<Args...>> storage;
    SignalToken(std::shared_ptr<detail::SignalCallbackStorage<Args...>> storage)
        : storage(storage)
    {
    }
    friend class Signal<Args...>;

public:
    SignalToken() = default;
};

template <typename... Args>
class Signal {
private:
    using storageT = detail::SignalCallbackStorage<Args...>;

    std::mutex _mutex;
    std::list<std::weak_ptr<storageT>> _callbacks;

public:
    using callbackT = std::function<void(Args...)>;
    using tokenT = SignalToken<Args...>;
    Signal() = default;
    Signal(const Signal&) = delete;
    Signal(Signal&&) = delete;

    // Connect a callback to this signal and return a token.
    // The token returned can be used to disconnect the callback.
    tokenT connect(callbackT callback, ConnectionMode mode = ConnectionMode::Direct)
    {
        std::unique_lock lock(_mutex);
        auto storage = std::make_shared<storageT>(std::move(callback), mode);
        _callbacks.push_back(storage);
        return storage;
    }

    // Disconnect a callback.
    // Token is the value returned by connect.
    void disconnect(tokenT token)
    {
        std::unique_lock lock(_mutex);
        _callbacks.remove_if(
            [&token](std::weak_ptr<storageT> ptr) {
                auto storage = ptr.lock();
                if (storage == nullptr) {
                    return true;
                }
                if (storage == token.storage) {
                    std::unique_lock storage_lock(storage->mutex);
                    storage->disconnected = true;
                    return true;
                }
                return false;
            });
    }

    // Call all callbacks with the given arguments from this thread.
    // Blocks until all callbacks are processed.
    void emit(Args... args)
    {
        std::list<std::weak_ptr<storageT>> temp_callbacks;
        {
            // Copy callbacks
            std::unique_lock lock(_mutex);
            temp_callbacks = _callbacks;
        }

        std::shared_ptr<std::tuple<Args...>> async_args;

        for (const auto& ptr : temp_callbacks) {
            auto storage = ptr.lock();
            if (storage == nullptr) {
                continue;
            }
            switch (storage->mode) {
            case ConnectionMode::Direct: {
                std::unique_lock storage_lock(storage->mutex);
                if (storage->disconnected) {
                    continue;
                }
                try {
                    storage->callback(args...);
                } catch (const std::exception& e) {
                    error(std::string("Error in callback: ") + e.what());
                } catch (...) {
                    error(std::string("Error in callback."));
                }
            } break;
            case ConnectionMode::Async: {
                if (async_args == nullptr) {
                    async_args = std::make_shared<std::tuple<Args...>>(std::forward<Args>(args)...);
                }
                detail::global_event_loop.submit([async_args, ptr]() {
                    auto storage = ptr.lock();
                    if (storage == nullptr) {
                        return;
                    }
                    std::unique_lock storage_lock(storage->mutex);
                    if (storage->disconnected) {
                        return;
                    }
                    try {
                        std::apply(storage->callback, *async_args);
                    } catch (const std::exception& e) {
                        error(std::string("Error in callback: ") + e.what());
                    } catch (...) {
                        error(std::string("Error in callback."));
                    }
                });
            } break;
            }
        }
    }

    ~Signal()
    {
        std::unique_lock lock(_mutex);
        for (const auto& ptr : _callbacks) {
            auto storage = ptr.lock();
            if (storage == nullptr) {
                continue;
            }
            std::unique_lock storage_lock(storage->mutex);
            storage->disconnected = true;
        }
    }
};

} // namespace Amulet
