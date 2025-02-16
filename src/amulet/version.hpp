#pragma once

#include <algorithm>
#include <cstdint>
#include <initializer_list>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include <amulet/dll.hpp>
#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

namespace Amulet {
typedef std::string PlatformType;
class VersionNumber {
private:
    std::vector<std::int64_t> vec;

public:
    const std::vector<std::int64_t>& get_vector() const { return vec; }

    template <typename... Args>
    VersionNumber(Args&&... args)
        : vec(std::forward<Args>(args)...)
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static VersionNumber deserialise(BinaryReader&);

    std::vector<std::int64_t>::const_iterator begin() const { return vec.begin(); }
    std::vector<std::int64_t>::const_iterator end() const { return vec.end(); }
    std::vector<std::int64_t>::const_reverse_iterator rbegin() const { return vec.rbegin(); }
    std::vector<std::int64_t>::const_reverse_iterator rend() const { return vec.rend(); }
    size_t size() const { return vec.size(); }
    AMULET_CORE_EXPORT std::int64_t operator[](size_t index) const;
    auto operator<=>(const VersionNumber& other) const
    {
        size_t max_len = std::max(vec.size(), other.size());
        std::int64_t v1, v2;
        for (size_t i = 0; i < max_len; i++) {
            v1 = (*this)[i];
            v2 = other[i];
            if (v1 < v2) {
                // Less than
                return std::strong_ordering::less;
            }
            if (v1 > v2) {
                // Greater than
                return std::strong_ordering::greater;
            }
        }
        // equal
        return std::strong_ordering::equal;
    }
    bool operator==(const VersionNumber& other) const
    {
        return (*this <=> other) == 0;
    }
    AMULET_CORE_EXPORT std::string toString() const;
    AMULET_CORE_EXPORT std::vector<std::int64_t> cropped_version() const;
    AMULET_CORE_EXPORT std::vector<std::int64_t> padded_version(size_t len) const;
};

class PlatformVersionContainer {
private:
    PlatformType platform;
    VersionNumber version;

public:
    const PlatformType& get_platform() const { return platform; }
    const VersionNumber& get_version() const { return version; }

    PlatformVersionContainer(
        const PlatformType& platform,
        const VersionNumber& version)
        : platform(platform)
        , version(version)
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static PlatformVersionContainer deserialise(BinaryReader&);

    auto operator<=>(const PlatformVersionContainer& other) const
    {
        auto cmp = platform <=> other.platform;
        if (cmp != 0) {
            return cmp;
        }
        return version <=> other.version;
    }
    bool operator==(const PlatformVersionContainer& other) const
    {
        return (*this <=> other) == 0;
    }
};

class VersionRange {
private:
    PlatformType platform;
    VersionNumber min_version;
    VersionNumber max_version;

public:
    const PlatformType& get_platform() const { return platform; }
    const VersionNumber& get_min_version() const { return min_version; }
    const VersionNumber& get_max_version() const { return max_version; }

    VersionRange(
        const PlatformType& platform,
        const VersionNumber& min_version,
        const VersionNumber& max_version)
        : platform(platform)
        , min_version(min_version)
        , max_version(max_version)
    {
        if (min_version > max_version) {
            throw std::invalid_argument("min_version must be less than or equal to max_version");
        }
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static VersionRange deserialise(BinaryReader&);

    AMULET_CORE_EXPORT bool contains(const PlatformType& platform_, const VersionNumber& version) const;
    AMULET_CORE_EXPORT bool operator==(const VersionRange&) const;
};

class VersionRangeContainer {
private:
    std::shared_ptr<const VersionRange> version_range;

public:
    std::shared_ptr<const VersionRange> get_version_range() const { return version_range; }

    VersionRangeContainer(
        std::shared_ptr<VersionRange> version_range)
        : version_range(version_range)
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static VersionRangeContainer deserialise(BinaryReader&);
};
}
