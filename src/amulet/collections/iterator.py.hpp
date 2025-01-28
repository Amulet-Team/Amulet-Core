#pragma once

#include <pybind11/pybind11.h>

#include <stdexcept>

namespace py = pybind11;

namespace Amulet {
namespace collections {
    class Iterator {
    public:
        virtual ~Iterator() = default;
        virtual py::object next() = 0;
    };

    // An iterator for the collections.abc.Sequence protocol.
    class PySequenceIterator : public Iterator {
    private:
        py::object obj;
        size_t index;
        std::ptrdiff_t step;

    public:
        PySequenceIterator(
            py::object obj,
            size_t start,
            std::ptrdiff_t step)
            : obj(obj)
            , index(start)
            , step(step)
        {
        }

        py::object next() override
        {
            if (index < 0 || py::len(obj) <= index) {
                throw py::stop_iteration("");
            }
            py::object item = obj.attr("__getitem__")(index);
            index += step;
            return item;
        }
    };

    // An iterator for a C++ map-like object.
    template <typename mapT>
    class MapIterator : public Iterator {
    private:
        py::object owner;
        const mapT& map;
        typename mapT::const_iterator begin;
        typename mapT::const_iterator end;
        typename mapT::const_iterator it;
        size_t size;

    public:
        MapIterator(const mapT& map, py::object owner = py::none())
            : owner(owner)
            , map(map)
            , begin(map.begin())
            , end(map.end())
            , it(map.begin())
            , size(map.size())
        {
        }

        py::object next() override
        {
            // This is not fool proof.
            // There are cases where this is true but the iterator is invalid.
            // The programmer should write good code and this will catch some of the bad cases.
            if (size != map.size() || begin != map.begin() || end != map.end()) {
                throw std::runtime_error("map changed size during iteration.");
            }
            if (it == end) {
                throw py::stop_iteration("");
            }
            return py::cast((it++)->first);
        }
    };

    template <typename mapT>
    py::object make_map_iterator(const mapT& map, py::object owner = py::none())
    {
        return py::cast(static_cast<std::shared_ptr<Iterator>>(
            std::make_shared<MapIterator<mapT>>(map, owner)));
    }

}
}
