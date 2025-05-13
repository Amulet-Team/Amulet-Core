#pragma once

#include <memory>
#include <optional>
#include <tuple>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/core/block/block.hpp>
#include <amulet/core/dll.hpp>
#include <amulet/core/palette/block_palette.hpp>
#include <amulet/core/version/version.hpp>

#include "section_array_map.hpp"

namespace Amulet {

class BlockComponentData {
private:
    std::shared_ptr<BlockPalette> _palette;
    std::shared_ptr<SectionArrayMap> _sections;

public:
    template <typename PaletteT, typename SectionsT>
    BlockComponentData(
        PaletteT&& palette,
        SectionsT&& sections)
        : _palette(
              [&palette] {
                  if constexpr (std::is_same_v<std::shared_ptr<BlockPalette>, std::decay_t<PaletteT>>) {
                      return std::forward<PaletteT>(palette);
                  } else {
                      return std::make_shared<BlockPalette>(palette);
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
    BlockComponentData(
        VersionRangeT&& version_range,
        const SectionShape& array_shape,
        const BlockStack& default_block)
        : BlockComponentData(
              std::make_shared<BlockPalette>(std::forward<VersionRangeT>(version_range)),
              std::make_shared<SectionArrayMap>(array_shape, static_cast<std::uint32_t>(0)))
    {
        _palette->block_stack_to_index(default_block);
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static BlockComponentData deserialise(BinaryReader&);

    BlockPalette& get_palette() const { return *_palette; }
    std::shared_ptr<BlockPalette> get_palette_ptr() const { return _palette; }
    SectionArrayMap& get_sections() const { return *_sections; }
    std::shared_ptr<SectionArrayMap> get_sections_ptr() const { return _sections; }
};

class BlockComponent {
private:
    std::optional<std::shared_ptr<BlockComponentData>> _value;

protected:
    // Null constructor
    BlockComponent() = default;

    // Default constructor
    template <typename VersionRangeT>
    void init(
        VersionRangeT&& version_range,
        const SectionShape& array_shape,
        const BlockStack& default_block)
    {
        _value = std::make_shared<BlockComponentData>(
            std::forward<VersionRangeT>(version_range),
            array_shape,
            default_block);
    }

    // Serialise the component data
    AMULET_CORE_EXPORT std::optional<std::string> serialise() const;
    // Deserialise the component
    AMULET_CORE_EXPORT void deserialise(std::optional<std::string>);

public:
    AMULET_CORE_EXPORT static const std::string ComponentID;
    AMULET_CORE_EXPORT std::shared_ptr<BlockComponentData> get_block();
    AMULET_CORE_EXPORT void set_block(std::shared_ptr<BlockComponentData> component);
};

} // namespace Amulet
