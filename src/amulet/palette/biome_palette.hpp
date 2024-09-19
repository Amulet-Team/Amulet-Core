#pragma once

#include <map>
#include <memory>
#include <stdexcept>

#include <amulet/version.hpp>
#include <amulet/biome.hpp>


namespace Amulet {

	struct PtrLess {
		bool operator()(std::shared_ptr<Biome> lhs, std::shared_ptr<Biome> rhs) const {
			return *lhs < *rhs;
		}
	};

	class BiomePalette : public VersionRangeContainer {
	private:
		std::vector<std::shared_ptr<Biome>> _index_to_biome;
		std::map<
			const std::shared_ptr<Biome>,
			size_t,
			PtrLess
		> _biome_to_index;
	public:
		const std::vector<std::shared_ptr<Biome>>& get_biomes() const { return _index_to_biome; }

		BiomePalette(std::shared_ptr<VersionRange> version_range) :
			VersionRangeContainer(version_range),
			_index_to_biome(),
			_biome_to_index() {}

		bool operator==(const BiomePalette& other) const {
			if (size() != other.size()) {
				return false;
			}
			for (size_t i = 0; i < size(); i++) {
				if (*_index_to_biome[i] != *other._index_to_biome[i]) {
					return false;
				}
			}
			return true;
		};

		size_t size() const { return _index_to_biome.size(); }

		std::shared_ptr<Biome> index_to_biome(size_t index) const {
			return _index_to_biome[index];
		};

		size_t biome_to_index(std::shared_ptr<Biome> biome) {
			auto it = _biome_to_index.find(biome);
			if (it != _biome_to_index.end()) {
				return it->second;
			}
			const auto& version_range = get_version_range();
			if (!version_range->contains(biome->get_platform(), *biome->get_version())) {
				throw std::invalid_argument(
					"Biome(\"" +
					biome->get_platform() +
					"\", " +
					biome->get_version()->toString() +
					") is incompatible with VersionRange(\"" +
					version_range->get_platform() +
					"\", " +
					version_range->get_min_version()->toString() +
					", " +
					version_range->get_max_version()->toString() +
					")."
				);
			}
			size_t index = _index_to_biome.size();
			_index_to_biome.push_back(biome);
			_biome_to_index[biome] = index;
			return index;
		};

		bool contains_biome(std::shared_ptr<Biome> biome) const {
			return _biome_to_index.contains(biome);
		}
	};

}
