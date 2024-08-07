#pragma once

#include <map>
#include <memory>
#include <stdexcept>

#include <amulet/version.hpp>
#include <amulet/block.hpp>


namespace Amulet {

	struct PtrLess {
		bool operator()(std::shared_ptr<BlockStack> lhs, std::shared_ptr<BlockStack> rhs) const {
			return *lhs < *rhs;
		}
	};

	class BlockPalette : public VersionRangeContainer {
	private:
		std::vector<std::shared_ptr<BlockStack>> index_to_block;
		std::map<
			const std::shared_ptr<BlockStack>, 
			size_t,
			PtrLess
		> block_to_index;
	public:
		const std::vector<std::shared_ptr<BlockStack>>& get_blocks() const { return index_to_block; }

		BlockPalette(std::shared_ptr<VersionRange> version_range) :
			VersionRangeContainer(version_range),
			index_to_block(),
			block_to_index() {}

		bool operator==(const BlockPalette& other) const {
			if (size() != other.size()) {
				return false;
			}
			for (size_t i = 0; i < size(); i++) {
				if (*index_to_block[i] != *other.index_to_block[i]) {
					return false;
				}
			}
			return true;
		};

		size_t size() const { return index_to_block.size(); }
		
		std::shared_ptr<BlockStack> index_to_block_stack(size_t index) const {
			if (index >= size()) {
				throw std::invalid_argument("Index is out of range");
			}
			return index_to_block[index]; 
		};

		size_t block_stack_to_index(std::shared_ptr<BlockStack> block) {
			auto it = block_to_index.find(block);
			if (it != block_to_index.end()) {
				return it->second;
			}
			const auto& version_range = get_version_range();
			for (const auto& block : block->get_blocks()) {
				if (!version_range->contains(block->get_platform(), *block->get_version())) {
					throw std::invalid_argument("BlockStack is incompatible with VersionRange.");
				}
			}
			size_t index = index_to_block.size();
			index_to_block.push_back(block);
			block_to_index[block] = index;
			return index;
		};

		bool contains_block(std::shared_ptr<BlockStack> block) const {
			return block_to_index.find(block) != block_to_index.end();
		}
	};

}
