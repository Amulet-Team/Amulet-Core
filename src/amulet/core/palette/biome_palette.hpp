#pragma once

#include <map>
#include <stdexcept>

#include <amulet/core/biome/biome.hpp>
#include <amulet/core/version/version.hpp>

namespace Amulet {

class BiomePalette : public VersionRangeContainer {
private:
    std::vector<Biome> _index_to_biome;
    std::map<Biome, size_t> _biome_to_index;

public:
    const std::vector<Biome>& get_biomes() const { return _index_to_biome; }

    template <typename VersionRangeT>
    BiomePalette(VersionRangeT&& version_range)
        : VersionRangeContainer(std::forward<VersionRangeT>(version_range))
        , _index_to_biome()
        , _biome_to_index()
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static BiomePalette deserialise(BinaryReader&);

    bool operator==(const BiomePalette& other) const
    {
        return _index_to_biome == other._index_to_biome;
    }

    size_t size() const { return _index_to_biome.size(); }

    const Biome& index_to_biome(size_t index) const
    {
        return _index_to_biome.at(index);
    }

    size_t biome_to_index(const Biome& biome)
    {
        auto it = _biome_to_index.find(biome);
        if (it != _biome_to_index.end()) {
            return it->second;
        }
        const auto& version_range = get_version_range();
        if (!version_range.contains(biome.get_platform(), biome.get_version())) {
            throw std::invalid_argument(
                "Biome(\"" + biome.get_platform() + "\", " + biome.get_version().toString() + ") is incompatible with VersionRange(\"" + version_range.get_platform() + "\", " + version_range.get_min_version().toString() + ", " + version_range.get_max_version().toString() + ").");
        }
        size_t index = _index_to_biome.size();
        _index_to_biome.push_back(biome);
        _biome_to_index[biome] = index;
        return index;
    }

    bool contains_biome(const Biome& biome) const
    {
        return _biome_to_index.contains(biome);
    }
};

}
