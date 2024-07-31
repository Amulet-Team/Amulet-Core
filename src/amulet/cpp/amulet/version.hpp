#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <sstream>
#include <memory>
#include <algorithm>
#include <iostream>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>


namespace Amulet {
    typedef std::string PlatformType;
    class VersionNumber {
        private:
            std::vector<std::int64_t> vec;
        public:
            const std::vector<std::int64_t>& get_vector() const { return vec; }

            VersionNumber(std::initializer_list<std::int64_t>);
            VersionNumber(std::vector<std::int64_t>);

            void serialise(Amulet::BinaryWriter&) const;
            static VersionNumber deserialise(Amulet::BinaryReader&);

            std::vector<std::int64_t>::const_iterator begin() const;
            std::vector<std::int64_t>::const_iterator end() const;
            std::vector<std::int64_t>::const_reverse_iterator rbegin() const;
            std::vector<std::int64_t>::const_reverse_iterator rend() const;
            size_t size() const;
            std::int64_t operator[](size_t index) const;
            auto operator<=>(const VersionNumber& other) const {
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
            bool operator==(const VersionNumber& other) const {
                return (*this <=> other) == 0;
            };
            std::string toString() const;
            std::vector<std::int64_t> cropped_version() const;
            std::vector<std::int64_t> padded_version(size_t len) const;
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
                const VersionNumber& version
            );

            void serialise(Amulet::BinaryWriter&) const;
            static PlatformVersionContainer deserialise(Amulet::BinaryReader&);

            auto operator<=>(const PlatformVersionContainer&) const = default;
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
                const VersionNumber& max_version
            );

            void serialise(Amulet::BinaryWriter&) const;
            static VersionRange deserialise(Amulet::BinaryReader&);

            bool contains(const PlatformType& platform_, const VersionNumber& version) const;
    };

    class VersionRangeContainer {
        private:
            VersionRange version_range;
        public:
            const VersionRange& get_version_range() const { return version_range; }

            VersionRangeContainer(
                const VersionRange& version_range
            );

            void serialise(Amulet::BinaryWriter&) const;
            static VersionRangeContainer deserialise(Amulet::BinaryReader&);
            
    };
}
