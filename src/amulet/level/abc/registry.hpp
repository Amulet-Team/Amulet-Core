#pragma once

#include <cstdint>
#include <map>
#include <shared_mutex>
#include <string>
#include <utility>

#include <amulet/dll.hpp>

namespace Amulet {

using NamespacedName = std::pair<std::string, std::string>;

// A registry from numerical id to namespaced name.
class IdRegistry {
private:
    std::shared_mutex _public_mutex;
    std::map<std::uint32_t, NamespacedName> _index_to_name;
    std::map<NamespacedName, std::uint32_t> _name_to_index;

public:
    AMULET_CORE_EXPORT IdRegistry() = default;

    // The public mutex.
    // Thread safe.
    AMULET_CORE_EXPORT std::shared_mutex& get_mutex();

    // Convert a numerical id to its namespaced id.
    // External shared lock required.
    AMULET_CORE_EXPORT NamespacedName numerical_id_to_namespace_id(std::uint32_t index) const;

    // Convert a namespaced id to its numerical id.
    // External shared lock required.
    AMULET_CORE_EXPORT std::uint32_t namespace_id_to_numerical_id(const NamespacedName& name) const;

    // Register a namespaced id to its numerical id.
    // External unique lock required.
    AMULET_CORE_EXPORT void register_id(std::uint32_t index, const NamespacedName& name);

    // The number of ids registered.
    // External shared lock required.
    AMULET_CORE_EXPORT size_t size() const;

    // A read-only view of ids registered.
    // External shared lock required.
    AMULET_CORE_EXPORT const std::map<std::uint32_t, NamespacedName>& ids() const;
};

} // namespace Amulet
