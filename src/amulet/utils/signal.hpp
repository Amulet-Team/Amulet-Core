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
        bool disconnected = false;

        SignalCallbackStorage(std::function<void(Args...)> callback)
            : callback(std::move(callback))
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
    tokenT connect(callbackT callback)
    {
        std::unique_lock lock(_mutex);
        auto storage = std::make_shared<storageT>(std::move(callback));
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

        for (const auto& ptr : temp_callbacks) {
            auto storage = ptr.lock();
            if (storage == nullptr) {
                continue;
            }
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
        }
    }

    // Submits all callbacks to the event loop for processing.
    // Returns immediately. Callbacks are processed asynchronously.
    // Note that args must remain valid until they are used.
    void emit_async(Args&&... args)
    {
        std::list<std::weak_ptr<storageT>> temp_callbacks;
        {
            // Copy callbacks
            std::unique_lock lock(_mutex);
            temp_callbacks = _callbacks;
        }

        // Copy the arguments once.
        auto args_ = std::make_shared<std::tuple<Args...>>(std::forward<Args>(args)...);

        for (const auto& ptr : temp_callbacks) {
            detail::global_event_loop.submit([args_, ptr]() {
                auto storage = ptr.lock();
                if (storage == nullptr) {
                    return;
                }
                std::unique_lock storage_lock(storage->mutex);
                if (storage->disconnected) {
                    return;
                }
                try {
                    std::apply(storage->callback, *args_);
                } catch (const std::exception& e) {
                    error(std::string("Error in callback: ") + e.what());
                } catch (...) {
                    error(std::string("Error in callback."));
                }
            });
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
