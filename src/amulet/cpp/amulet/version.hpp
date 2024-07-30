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
            const std::vector<std::int64_t>& get_vector() const;

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
            bool operator==(const VersionNumber& other) const;
            bool operator!=(const VersionNumber& other) const;
            bool operator<(const VersionNumber& other) const;
            bool operator>(const VersionNumber& other) const;
            bool operator<=(const VersionNumber& other) const;
            bool operator>=(const VersionNumber& other) const;
            std::string toString() const;
            std::vector<std::int64_t> cropped_version() const;
            std::vector<std::int64_t> padded_version(size_t len) const;
    };

    class PlatformVersionContainer {
        private:
            PlatformType platform;
            VersionNumber version;
        public:
            const PlatformType& get_platform() const;
            const VersionNumber& get_version() const;

            PlatformVersionContainer(
                const PlatformType& platform,
                const VersionNumber& version
            );

            void serialise(Amulet::BinaryWriter&) const;
            static PlatformVersionContainer deserialise(Amulet::BinaryReader&);
    };

    class VersionRange {
        private:
            PlatformType platform;
            VersionNumber min_version;
            VersionNumber max_version;
        public:
            const PlatformType& get_platform() const;
            const VersionNumber& get_min_version() const;
            const VersionNumber& get_max_version() const;

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
            const VersionRange& get_version_range() const;

            VersionRangeContainer(
                const VersionRange& version_range
            );

            void serialise(Amulet::BinaryWriter&) const;
            static VersionRangeContainer deserialise(Amulet::BinaryReader&);
            
    };
}
