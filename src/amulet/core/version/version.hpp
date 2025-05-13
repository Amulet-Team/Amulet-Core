#pragma once

#include <algorithm>
#include <cstdint>
#include <initializer_list>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/core/dll.hpp>

namespace Amulet {

typedef std::string PlatformType;

// This class is designed to store semantic versions and data versions and allow comparisons between them.
// It is a wrapper around std::vector<std::int64_t> with special comparison handling.
// The version can contain zero to max(int64) values.
// Undefined trailing values are implied zeros. 1.1 == 1.1.0
// All methods are thread safe.
class VersionNumber {
private:
    std::vector<std::int64_t> _vec;

public:
    // Get the underlying vector.
    // Thread safe.
    const std::vector<std::int64_t>& get_vector() const { return _vec; }

    // Constructors
    template <typename... Args>
        requires std::is_constructible_v<std::vector<std::int64_t>, Args...>
    VersionNumber(Args&&... args)
        : _vec(std::forward<Args>(args)...)
    {
    }

    VersionNumber(std::initializer_list<std::int64_t> args)
        : _vec(args)
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static VersionNumber deserialise(BinaryReader&);

    // Iterators
    std::vector<std::int64_t>::const_iterator begin() const { return _vec.begin(); }
    std::vector<std::int64_t>::const_iterator end() const { return _vec.end(); }
    std::vector<std::int64_t>::const_reverse_iterator rbegin() const { return _vec.rbegin(); }
    std::vector<std::int64_t>::const_reverse_iterator rend() const { return _vec.rend(); }

    // Capacity
    size_t size() const { return _vec.size(); }

    // Element access
    std::int64_t operator[](size_t index) const {
        if (index >= _vec.size()) {
            return 0;
        }
        return _vec[index];
    }

    // Comparison
    auto operator<=>(const VersionNumber& other) const
    {
        size_t max_len = std::max(_vec.size(), other.size());
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
    PlatformType _platform;
    VersionNumber _version;

public:
    // Get the platform identifier.
    const PlatformType& get_platform() const { return _platform; }

    // Get the version number.
    const VersionNumber& get_version() const { return _version; }

    template <typename PlatformT, typename VersionNumberT>
    PlatformVersionContainer(
        PlatformT&& platform,
        VersionNumberT&& version)
        : _platform(std::forward<PlatformT>(platform))
        , _version(std::forward<VersionNumberT>(version))
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static PlatformVersionContainer deserialise(BinaryReader&);

    // Comparison operators
    auto operator<=>(const PlatformVersionContainer& other) const
    {
        auto cmp = _platform <=> other._platform;
        if (cmp != 0) {
            return cmp;
        }
        return _version <=> other._version;
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
    PlatformType _platform;
    VersionNumber _min_version;
    VersionNumber _max_version;

public:
    // Get the platform identifier.
    const PlatformType& get_platform() const { return _platform; }

    // Get the minimum version number
    const VersionNumber& get_min_version() const { return _min_version; }

    // Get the maximum version number
    const VersionNumber& get_max_version() const { return _max_version; }

    template <typename PlatformT, typename MinVersionT, typename MaxVersionT>
    VersionRange(
        PlatformT&& platform,
        MinVersionT&& min_version,
        MaxVersionT&& max_version)
        : _platform(std::forward<PlatformT>(platform))
        , _min_version(std::forward<MinVersionT>(min_version))
        , _max_version(std::forward<MaxVersionT>(max_version))
    {
        if (_min_version > _max_version) {
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
    VersionRange _version_range;

public:
    // Get the version range.
    const VersionRange& get_version_range() const { return _version_range; }

    template <typename VersionRangeT>
    VersionRangeContainer(
        VersionRangeT&& version_range)
        : _version_range(std::forward<VersionRangeT>(version_range))
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static VersionRangeContainer deserialise(BinaryReader&);
};
}
