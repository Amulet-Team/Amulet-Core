#pragma once

#include <algorithm>
#include <cstdint>
#include <initializer_list>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include <amulet/core/dll.hpp>
#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

namespace Amulet {

typedef std::string PlatformType;

// This class is designed to store semantic versions and data versions and allow comparisons between them.
// It is a wrapper around std::vector<std::int64_t> with special comparison handling.
// The version can contain zero to max(int64) values.
// Undefined trailing values are implied zeros. 1.1 == 1.1.0
// All methods are thread safe.
class VersionNumber {
private:
    std::vector<std::int64_t> vec;

public:
    // Get the underlying vector.
    // Thread safe.
    const std::vector<std::int64_t>& get_vector() const { return vec; }

    // Constructors
    template <typename... Args>
        requires std::is_constructible_v<std::vector<std::int64_t>, Args...>
    VersionNumber(Args&&... args)
        : vec(std::forward<Args>(args)...)
    {
    }

    VersionNumber(std::initializer_list<std::int64_t> args)
        : vec(args)
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static VersionNumber deserialise(BinaryReader&);

    // Iterators
    std::vector<std::int64_t>::const_iterator begin() const { return vec.begin(); }
    std::vector<std::int64_t>::const_iterator end() const { return vec.end(); }
    std::vector<std::int64_t>::const_reverse_iterator rbegin() const { return vec.rbegin(); }
    std::vector<std::int64_t>::const_reverse_iterator rend() const { return vec.rend(); }
    
    // Capacity
    size_t size() const { return vec.size(); }

    // Element access
    AMULET_CORE_EXPORT std::int64_t operator[](size_t index) const;
    
    // Comparison
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

    // Convert the value to its string representation eg "1.1"
    AMULET_CORE_EXPORT std::string toString() const;

    // The version number with trailing zeros cut off.
    AMULET_CORE_EXPORT std::vector<std::int64_t> cropped_version() const;

    // Get the version number cropped or padded with zeros to the given length.
    AMULET_CORE_EXPORT std::vector<std::int64_t> padded_version(size_t len) const;
};

// A class storing platform identifier and version number.
// Thread safe.
class PlatformVersionContainer {
private:
    PlatformType platform;
    VersionNumber version;

public:
    // Get the platform identifier.
    const PlatformType& get_platform() const { return platform; }

    // Get the version number.
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

    // Comparison operators
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

// A class storing platform identifier and minimum and maximum version numbers.
// Thread safe.
class VersionRange {
private:
    PlatformType platform;
    VersionNumber min_version;
    VersionNumber max_version;

public:
    // Get the platform identifier.
    const PlatformType& get_platform() const { return platform; }

    // Get the minimum version number
    const VersionNumber& get_min_version() const { return min_version; }

    // Get the maximum version number
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

    // Check if the platform is equal and the version number is within the range.
    AMULET_CORE_EXPORT bool contains(const PlatformType& platform_, const VersionNumber& version) const;
    
    // Equality operator
    AMULET_CORE_EXPORT bool operator==(const VersionRange&) const;
};

// A class that contains a version range.
class VersionRangeContainer {
private:
    VersionRange version_range;

public:
    // Get the version range.
    const VersionRange& get_version_range() const { return version_range; }

    VersionRangeContainer(
        const VersionRange& version_range)
        : version_range(version_range)
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static VersionRangeContainer deserialise(BinaryReader&);
};
}
