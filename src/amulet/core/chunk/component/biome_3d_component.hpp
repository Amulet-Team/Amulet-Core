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

class AMULET_CORE_EXPORT Biome3DStorage {
private:
    std::shared_ptr<BiomePalette> _palette;
    std::shared_ptr<SectionArrayMap> _sections;

public:
    template <typename PaletteT, typename SectionsT>
    Biome3DStorage(
        PaletteT&& palette,
        SectionsT&& sections)
        : _palette(
              [&palette] {
                  if constexpr (std::is_same_v<std::shared_ptr<BiomePalette>, std::decay_t<PaletteT>>) {
                      return std::forward<PaletteT>(palette);
                  } else {
                      return std::make_shared<BiomePalette>(palette);
                  }
              }())
        , _sections(
              [&sections] {
                  if constexpr (std::is_same_v<std::shared_ptr<SectionArrayMap>, std::decay_t<SectionsT>>) {
                      return std::forward<SectionsT>(sections);
                  } else {
                      return std::make_shared<SectionArrayMap>(sections);
                  }
              }())
    {
    }

    template <typename VersionRangeT>
    Biome3DStorage(
        VersionRangeT&& version_range,
        const SectionShape& array_shape,
        const Biome& default_biome)
        : Biome3DStorage(
              std::make_shared<BiomePalette>(std::forward<VersionRangeT>(version_range)),
              std::make_shared<SectionArrayMap>(array_shape, static_cast<std::uint32_t>(0)))
    {
        _palette->biome_to_index(default_biome);
    }

    BiomePalette& get_palette() { return *_palette; }
    std::shared_ptr<BiomePalette> get_palette_ptr() { return _palette; }
    SectionArrayMap& get_sections() { return *_sections; }
    std::shared_ptr<SectionArrayMap> get_sections_ptr() { return _sections; }

    void serialise(BaseBinaryWriter&) const;
    static Biome3DStorage deserialise(BinaryReader&);
};

class AMULET_CORE_EXPORT Biome3DComponent {
private:
    std::optional<std::shared_ptr<Biome3DStorage>> _value;

protected:
    // Null constructor
    Biome3DComponent() = default;

    // Default constructor
    template <typename VersionRangeT>
    void init(
        VersionRangeT&& version_range,
        const SectionShape& array_shape,
        const Biome& default_biome)
    {
        _value = std::make_shared<Biome3DStorage>(
            std::forward<VersionRangeT>(version_range),
            array_shape,
            default_biome);
    }

    // Serialise the component data
    std::optional<std::string> serialise() const;
    // Deserialise the component
    void deserialise(std::optional<std::string>);

public:
    static const std::string ComponentID;
    std::shared_ptr<Biome3DStorage> get_biome_storage();
    void set_biome_storage(std::shared_ptr<Biome3DStorage> component);
};

} // namespace Amulet
