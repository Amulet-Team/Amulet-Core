#pragma once

#include <list>
#include <memory>
#include <set>

namespace Amulet {

namespace detail {
    template <typename C, typename T>
    void for_each(C& l, std::function<void(T&)> f)
    {
        auto it = l.begin();
        while (it != l.end()) {
            auto ptr = it->lock();
            if (ptr) {
                f(*ptr);
                it++;
            } else {
                it = l.erase(it);
            }
        }
    }
}

template <typename T>
using WeakList = std::list<std::weak_ptr<T>>;

template <typename T>
void for_each(WeakList<T>& l, std::function<void(T&)> f)
{
    detail::for_each(l, f);
}

template <typename T>
using WeakSet = std::set<std::weak_ptr<T>, std::owner_less<std::weak_ptr<T>>>;

template <typename T>
void for_each(WeakSet<T>& s, std::function<void(T&)> f)
{
    detail::for_each(s, f);
}

} // namespace Amulet
