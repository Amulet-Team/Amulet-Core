#pragma once

#include <functional>
#include <iostream>
#include <list>
#include <mutex>

namespace Amulet {

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

// template <typename... Args>
// class Signal;

template <typename... Args>
class SignalToken {
    // friend class Signal<Args...>;

    // private:
public:
    std::shared_ptr<SignalCallbackStorage<Args...>> storage;
    SignalToken(std::shared_ptr<SignalCallbackStorage<Args...>> storage)
        : storage(storage)
    {
    }
};

template <typename... Args>
class Signal {
    using callbackT = std::function<void(Args...)>;
    using storageT = SignalCallbackStorage<Args...>;
    using tokenT = SignalToken<Args...>;

private:
    std::mutex _mutex;
    std::list<std::shared_ptr<storageT>> _callbacks;

public:
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
            [&token](std::shared_ptr<storageT> storage) {
                if (storage == token.storage) {
                    std::unique_lock storage_lock(storage->mutex);
                    storage->disconnected = true;
                }
                return false;
            });
    }

    // Call all callbacks with the given arguments.
    void emit(Args... args)
    {
        std::list<std::shared_ptr<storageT>> temp_callbacks;
        {
            // Copy callbacks
            std::unique_lock lock(_mutex);
            temp_callbacks = _callbacks;
        }

        for (const auto& storage : temp_callbacks) {
            std::unique_lock storage_lock(storage->mutex);
            if (storage->disconnected) {
                continue;
            }
            try {
                storage->callback(args...);
            } catch (const std::exception& e) {
                // TODO: hook this up to a logging system.
                std::cout << e.what() << std::endl;
            } catch (...) {
                std::cout << "Error in callback" << std::endl;
            }
        }
    }

    ~Signal()
    {
        std::unique_lock lock(_mutex);
        for (const auto& storage : _callbacks) {
            std::unique_lock storage_lock(storage->mutex);
            storage->disconnected = true;
        }
    }
};

} // namespace Amulet
