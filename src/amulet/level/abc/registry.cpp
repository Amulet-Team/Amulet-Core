#include <shared_mutex>
#include <stdexcept>
#include <string>

#include "registry.hpp"

namespace Amulet {

std::shared_mutex& IdRegistry::get_mutex()
{
    return _public_mutex;
}

NamespacedName IdRegistry::numerical_id_to_namespace_id(std::uint32_t index) const
{
    return _index_to_name.at(index);
}

std::uint32_t IdRegistry::namespace_id_to_numerical_id(const NamespacedName& name) const
{
    return _name_to_index.at(name);
}

void IdRegistry::register_id(std::uint32_t index, const NamespacedName& name)
{
    if (_index_to_name.contains(index)) {
        throw std::runtime_error("index " + std::to_string(index) + " has already been registered.");
    }
    if (_name_to_index.contains(name)) {
        throw std::runtime_error(std::get<0>(name) + ":" + std::get<1>(name) + " has already been registered.");
    }
    _index_to_name.emplace(index, name);
    _name_to_index.emplace(name, index);
}

size_t IdRegistry::size() const
{
    return _index_to_name.size();
}

const std::map<std::uint32_t, NamespacedName>& IdRegistry::ids() const
{
    return _index_to_name;
}

} // namespace Amulet
