#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <sstream>
#include <memory>
#include <algorithm>


namespace Amulet {
    typedef std::string PlatformType;
    class VersionNumber {
        private:
            const std::vector<std::int64_t> value;
        public:
            VersionNumber(std::initializer_list<std::int64_t> value);
            VersionNumber(std::vector<std::int64_t> value);
            // serialise
            // deserialise
            std::vector<std::int64_t>::const_iterator begin() const;
            std::vector<std::int64_t>::const_iterator end() const;
            std::vector<std::int64_t>::const_reverse_iterator rbegin() const;
            std::vector<std::int64_t>::const_reverse_iterator rend() const;
            size_t size() const;
            std::int64_t operator[](size_t index) const;
            bool operator==(const VersionNumber& other) const;
            bool operator!=(const VersionNumber& other) const;
            bool operator<(const VersionNumber& other) const;
            bool operator>(const VersionNumber& other) const;
            bool operator<=(const VersionNumber& other) const;
            bool operator>=(const VersionNumber& other) const;
            std::string toString() const;
            std::string repr() const;
            std::vector<std::int64_t> cropped_version() const;
            std::vector<std::int64_t> padded_version(size_t len) const;
    };

    class PlatformVersionContainer {
        public:
            const PlatformType platform;
            const VersionNumber version;

            PlatformVersionContainer(
                const PlatformType& platform,
                const VersionNumber& version
            );

            std::string repr() const;
    };

    class VersionRange {
        public:
            const PlatformType platform;
            const VersionNumber min_version;
            const VersionNumber max_version;

            VersionRange(
                const PlatformType& platform,
                const VersionNumber& min_version,
                const VersionNumber& max_version
            );

            std::string repr() const;
            bool contains(const PlatformType& platform_, const VersionNumber& version) const;
    };

    class VersionRangeContainer {
        public:
            const VersionRange version_range;

            VersionRangeContainer(
                const VersionRange& version_range
            );

            std::string repr() const;
    };
}
