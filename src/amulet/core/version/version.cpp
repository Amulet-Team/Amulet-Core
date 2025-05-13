#include <compare>
#include <cstdint>
#include <stdexcept>

#include <amulet/core/dll.hpp>

#include "version.hpp"

namespace Amulet {

void VersionNumber::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    writer.write_numeric<std::uint64_t>(_vec.size());
    for (const std::int64_t& v : _vec) {
        writer.write_numeric<std::int64_t>(v);
    }
}

VersionNumber VersionNumber::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        std::uint64_t count;
        reader.read_numeric_into(count);
        std::vector<std::int64_t> vec(count);
        for (size_t i = 0; i < count; i++) {
            reader.read_numeric_into<std::int64_t>(vec[i]);
        }
        return vec;
    }
    default:
        throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
    }
}

std::string VersionNumber::toString() const
{
    std::ostringstream oss;
    for (size_t i = 0; i < _vec.size(); ++i) {
        if (i > 0) {
            oss << '.';
        }
        oss << _vec[i];
    }
    return oss.str();
}

std::vector<std::int64_t> VersionNumber::cropped_version() const
{
    bool found_non_zero = false;
    std::vector<std::int64_t> out;
    for (auto it = _vec.rbegin(); it != _vec.rend(); ++it) {
        if (found_non_zero) {
            out.push_back(*it);
        } else if (*it != 0) {
            found_non_zero = true;
            out.push_back(*it);
        }
    }
    std::reverse(out.begin(), out.end());
    return out;
}

std::vector<std::int64_t> VersionNumber::padded_version(size_t len) const
{
    std::vector<std::int64_t> out(len);
    for (size_t i = 0; i < len; i++) {
        out[i] = (*this)[i];
    }
    return out;
}

void PlatformVersionContainer::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    writer.write_size_and_bytes(_platform);
    _version.serialise(writer);
}

PlatformVersionContainer PlatformVersionContainer::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        std::string platform { reader.read_size_and_bytes() };
        auto version = VersionNumber::deserialise(reader);
        return { platform, version };
    }
    default:
        throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
    }
}

void VersionRange::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    writer.write_size_and_bytes(_platform);
    _min_version.serialise(writer);
    _max_version.serialise(writer);
}

VersionRange VersionRange::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        std::string platform { reader.read_size_and_bytes() };
        auto min_version = VersionNumber::deserialise(reader);
        auto max_version = VersionNumber::deserialise(reader);
        return { platform, min_version, max_version };
    }
    default:
        throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
    }
}

bool VersionRange::contains(const PlatformType& platform, const VersionNumber& version) const
{
    return _platform == platform && _min_version <= version && version <= _max_version;
}

bool VersionRange::operator==(const VersionRange& other) const
{
    return _platform == other._platform && _min_version == other._min_version && _max_version == other._max_version;
}

void VersionRangeContainer::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    _version_range.serialise(writer);
}

VersionRangeContainer VersionRangeContainer::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        return VersionRange::deserialise(reader);
    }
    default:
        throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
    }
}

} // namespace Amulet
