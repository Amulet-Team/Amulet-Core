#pragma once

#include <cstdint>
#include <memory>
#include <optional>
#include <tuple>

#include <amulet/core/biome/biome.hpp>
#include <amulet/core/dll.hpp>
#include <amulet/core/palette/biome_palette.hpp>
#include <amulet/core/version/version.hpp>

#include "section_array_map.hpp"

namespace Amulet {

class Biome3DStorage {
private:
    std::shared_ptr<BiomePalette> _palette;
    std::shared_ptr<SectionArrayMap> _sections;

public:
    AMULET_CORE_EXPORT Biome3DStorage(
        const VersionRange& version_range,
        const SectionShape& array_shape,
        const Biome& default_biome);
    AMULET_CORE_EXPORT std::shared_ptr<BiomePalette> get_palette();
    AMULET_CORE_EXPORT std::shared_ptr<SectionArrayMap> get_sections();
};

class Biome3DComponent {
private:
    std::optional<std::shared_ptr<Biome3DStorage>> _value;

protected:
    // Null constructor
    AMULET_CORE_EXPORT Biome3DComponent() = default;
    // Default constructor
    AMULET_CORE_EXPORT void init(
        const VersionRange& version_range,
        const SectionShape& array_shape,
        const Biome& default_biome);

    // Serialise the component data
    AMULET_CORE_EXPORT std::optional<std::string> serialise() const;
    // Deserialise the component
    AMULET_CORE_EXPORT void deserialise(std::optional<std::string>);

public:
    AMULET_CORE_EXPORT static const std::string ComponentID;
    AMULET_CORE_EXPORT std::shared_ptr<Biome3DStorage> get_biome();
    AMULET_CORE_EXPORT void set_biome(std::shared_ptr<Biome3DStorage> component);
};

} // namespace Amulet
