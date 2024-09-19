#pragma once

#include <map>
#include <memory>
#include <stdexcept>

#include <amulet/version.hpp>
#include <amulet/block.hpp>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>


namespace Amulet {

	struct PtrLess {
		bool operator()(std::shared_ptr<BlockStack> lhs, std::shared_ptr<BlockStack> rhs) const {
			return *lhs < *rhs;
		}
	};

	class BlockPalette : public VersionRangeContainer {
	private:
		std::vector<std::shared_ptr<BlockStack>> _index_to_block;
		std::map<
			const std::shared_ptr<BlockStack>, 
			size_t,
			PtrLess
		> _block_to_index;
	public:
		const std::vector<std::shared_ptr<BlockStack>>& get_blocks() const { return _index_to_block; }

		BlockPalette(std::shared_ptr<VersionRange> version_range) :
			VersionRangeContainer(version_range),
			_index_to_block(),
			_block_to_index() {}

		void serialise(BinaryWriter&) const;
		static std::shared_ptr<BlockPalette> deserialise(BinaryReader&);

		bool operator==(const BlockPalette& other) const {
			if (size() != other.size()) {
				return false;
			}
			for (size_t i = 0; i < size(); i++) {
				if (*_index_to_block[i] != *other._index_to_block[i]) {
					return false;
				}
			}
			return true;
		};

		size_t size() const { return _index_to_block.size(); }
		
		std::shared_ptr<BlockStack> index_to_block_stack(size_t index) const {
			return _index_to_block[index];
		};

		size_t block_stack_to_index(std::shared_ptr<BlockStack> block) {
			auto it = _block_to_index.find(block);
			if (it != _block_to_index.end()) {
				return it->second;
			}
			auto version_range = get_version_range();
			for (const auto& block : block->get_blocks()) {
				if (!version_range->contains(block->get_platform(), *block->get_version())) {
					throw std::invalid_argument(
						"BlockStack(\"" + 
						block->get_platform() +
						"\", " +
						block->get_version()->toString() +
						") is incompatible with VersionRange(\"" +
						version_range->get_platform() +
						"\", " +
						version_range->get_min_version()->toString() +
						", " +
						version_range->get_max_version()->toString() +
						")."
					);
				}
			}
			size_t index = _index_to_block.size();
			_index_to_block.push_back(block);
			_block_to_index[block] = index;
			return index;
		};

		bool contains_block(std::shared_ptr<BlockStack> block) const {
			return _block_to_index.contains(block);
		}
	};

}
