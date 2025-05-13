#pragma once

#include <map>
#include <stdexcept>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/core/block/block.hpp>
#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

namespace Amulet {

class BlockPalette : public VersionRangeContainer {
private:
    std::vector<BlockStack> _index_to_block;
    std::map<BlockStack, size_t> _block_to_index;

public:
    const std::vector<BlockStack>& get_blocks() const { return _index_to_block; }

    template <typename VersionRangeT>
    BlockPalette(VersionRangeT&& version_range)
        : VersionRangeContainer(std::forward<VersionRangeT>(version_range))
        , _index_to_block()
        , _block_to_index()
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static BlockPalette deserialise(BinaryReader&);

    bool operator==(const BlockPalette& other) const
    {
        return _index_to_block == other._index_to_block;
    }

    size_t size() const { return _index_to_block.size(); }

    const BlockStack& index_to_block_stack(size_t index) const
    {
        return _index_to_block.at(index);
    }

    size_t block_stack_to_index(const BlockStack& block_stack)
    {
        auto it = _block_to_index.find(block_stack);
        if (it != _block_to_index.end()) {
            return it->second;
        }
        auto version_range = get_version_range();
        for (const auto& block : block_stack.get_blocks()) {
            if (!version_range.contains(block.get_platform(), block.get_version())) {
                throw std::invalid_argument(
                    "BlockStack(\"" + block.get_platform() + "\", " + block.get_version().toString() + ") is incompatible with VersionRange(\"" + version_range.get_platform() + "\", " + version_range.get_min_version().toString() + ", " + version_range.get_max_version().toString() + ").");
            }
        }
        size_t index = _index_to_block.size();
        _index_to_block.push_back(block_stack);
        _block_to_index.emplace(block_stack, index);
        return index;
    }

    bool contains_block(const BlockStack& block) const
    {
        return _block_to_index.contains(block);
    }
};

}
