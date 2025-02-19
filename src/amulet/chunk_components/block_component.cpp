#include <amulet/chunk_components/block_component.hpp>
#include <amulet/dll.hpp>

namespace Amulet {

// BlockComponentData
BlockComponentData::BlockComponentData(
    const VersionRange& version_range,
    const SectionShape& array_shape,
    const BlockStack& default_block)
    : _palette(std::make_shared<BlockPalette>(version_range))
    , _sections(std::make_shared<SectionArrayMap>(array_shape, static_cast<std::uint32_t>(0)))
{
    _palette->block_stack_to_index(default_block);
}

BlockComponentData::BlockComponentData(
    std::shared_ptr<BlockPalette> palette,
    std::shared_ptr<SectionArrayMap> sections)
    : _palette(palette)
    , _sections(sections)
{
}

void BlockComponentData::serialise(BinaryWriter& writer) const
{
    writer.writeNumeric<std::uint8_t>(1);
    get_palette()->serialise(writer);
    get_sections()->serialise(writer);
}

BlockComponentData BlockComponentData::deserialise(BinaryReader& reader)
{
    auto version = reader.readNumeric<std::uint8_t>();
    switch (version) {
    case 1: {
        auto palette = Amulet::deserialise_shared<BlockPalette>(reader);
        auto sections = Amulet::deserialise_shared<SectionArrayMap>(reader);
        return { palette, sections };
    }
    default:
        throw std::invalid_argument("Unsupported BlockComponentData version " + std::to_string(version));
    }
}

std::shared_ptr<BlockPalette> BlockComponentData::get_palette() const
{
    return _palette;
}

std::shared_ptr<SectionArrayMap> BlockComponentData::get_sections() const
{
    return _sections;
}

// BlockComponent
void BlockComponent::init(
    const VersionRange& version_range,
    const SectionShape& array_shape,
    const BlockStack& default_block)
{
    _value = std::make_shared<BlockComponentData>(version_range, array_shape, default_block);
}

std::optional<std::string> BlockComponent::serialise() const
{
    if (_value) {
        return Amulet::serialise(**_value);
    } else {
        return std::nullopt;
    }
}

void BlockComponent::deserialise(std::optional<std::string> data)
{
    if (data) {
        _value = Amulet::deserialise_shared<BlockComponentData>(*data);
    } else {
        _value = std::nullopt;
    }
}

const std::string BlockComponent::ComponentID = "Amulet::BlockComponent";

std::shared_ptr<BlockComponentData> BlockComponent::get_block()
{
    if (_value) {
        return *_value;
    }
    throw std::runtime_error("BlockComponent has not been loaded.");
}

void BlockComponent::set_block(std::shared_ptr<BlockComponentData> component)
{
    if (_value) {
        if ((*_value)->get_sections()->get_array_shape() != component->get_sections()->get_array_shape()) {
            throw std::invalid_argument("New block array shape does not match old array shape.");
        }
        if ((*_value)->get_palette()->get_version_range() != component->get_palette()->get_version_range()) {
            throw std::invalid_argument("New block version range does not match old version range.");
        }
        _value = component;
    } else {
        throw std::runtime_error("BlockComponent has not been loaded.");
    }
}

} // namespace Amulet
