#pragma once

#include <pybind11/pybind11.h>

#include <memory>

namespace Amulet {

// A custom shared ptr that releases the GIL before freeing the resource.
template <typename T>
class nogil_shared_ptr {
private:
    std::shared_ptr<T> ptr;

public:
    template <typename... Args>
    nogil_shared_ptr(Args&&... args)
        : ptr(std::forward<Args>(args)...)
    {
    }

    ~nogil_shared_ptr()
    {
        pybind11::gil_scoped_release nogil;
        ptr.reset();
    }

    T& operator*() const noexcept { return *ptr; }
    T* operator->() const noexcept { return ptr.get(); }
    operator std::shared_ptr<T>() const noexcept { return ptr; }
    T* get() const noexcept { return ptr.get(); }
};

} // namespace Amulet

PYBIND11_DECLARE_HOLDER_TYPE(T, Amulet::nogil_shared_ptr<T>)
