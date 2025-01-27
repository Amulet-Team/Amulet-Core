#pragma once

#include <memory>
#include <optional>
#include <tuple>

#include <amulet/block.hpp>
#include <amulet/chunk_components/section_array_map.hpp>
#include <amulet/dll.hpp>
#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>
#include <amulet/palette/block_palette.hpp>
#include <amulet/version.hpp>

namespace Amulet {

class BlockComponentData {
private:
    std::shared_ptr<BlockPalette> _palette;
    std::shared_ptr<SectionArrayMap> _sections;

public:
    AMULET_CORE_EXPORT BlockComponentData(
        std::shared_ptr<VersionRange> version_range,
        const SectionShape& array_shape,
        std::shared_ptr<BlockStack> default_block);
    AMULET_CORE_EXPORT BlockComponentData(
        std::shared_ptr<BlockPalette> palette,
        std::shared_ptr<SectionArrayMap> sections);
    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static std::shared_ptr<BlockComponentData> deserialise(BinaryReader&);
    AMULET_CORE_EXPORT std::shared_ptr<BlockPalette> get_palette() const;
    AMULET_CORE_EXPORT std::shared_ptr<SectionArrayMap> get_sections() const;
};

class BlockComponent {
private:
    std::optional<std::shared_ptr<BlockComponentData>> _value;

protected:
    // Null constructor
    AMULET_CORE_EXPORT BlockComponent() = default;
    // Default constructor
    AMULET_CORE_EXPORT void init(
        std::shared_ptr<VersionRange> version_range,
        const SectionShape& array_shape,
        std::shared_ptr<BlockStack> default_block);

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
