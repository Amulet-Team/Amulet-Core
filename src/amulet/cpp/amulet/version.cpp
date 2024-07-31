#include <stdexcept>
#include <cstdint>
#include <compare>

#include <amulet/version.hpp>


namespace Amulet {
    VersionNumber::VersionNumber(std::initializer_list<std::int64_t> vec): vec(vec) {};
    VersionNumber::VersionNumber(std::vector<std::int64_t> vec): vec(vec) {};

    void VersionNumber::serialise(Amulet::BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeNumeric<std::uint64_t>(vec.size());
        for (const std::int64_t& v : vec){
            writer.writeNumeric<std::int64_t>(v);
        }
    }
    VersionNumber VersionNumber::deserialise(Amulet::BinaryReader& reader){
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
            case 1:
            {
                std::uint64_t count;
                reader.readNumericInto(count);
                std::vector<std::int64_t> vec(count);
                for (size_t i = 0; i < count; i++) {
                    reader.readNumericInto<std::int64_t>(vec[i]);
                }
                return VersionNumber(vec);
            }
            default:
                throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }

    std::vector<std::int64_t>::const_iterator VersionNumber::begin() const {
        return vec.begin();
    }

    std::vector<std::int64_t>::const_iterator VersionNumber::end() const {
        return vec.end();
    }

    std::vector<std::int64_t>::const_reverse_iterator VersionNumber::rbegin() const {
        return vec.rbegin();
    }

    std::vector<std::int64_t>::const_reverse_iterator VersionNumber::rend() const {
        return vec.rend();
    }

    size_t VersionNumber::size() const {
        return vec.size();
    }

    std::int64_t VersionNumber::operator[](size_t index) const {
        if (index >= vec.size()) {
            return 0;
        }
        return vec[index];
    }

    std::string VersionNumber::toString() const {
        std::ostringstream oss;
        for (size_t i = 0; i < vec.size(); ++i) {
            if (i > 0){
                oss << '.';
            }
            oss << vec[i];
        }
        return oss.str();
    }

    std::vector<std::int64_t> VersionNumber::cropped_version() const {
        bool found_non_zero = false;
        std::vector<std::int64_t> out;
        for (auto it = vec.rbegin(); it != vec.rend(); ++it) {
            if (found_non_zero){
                out.push_back(*it);
            } else if (*it != 0) {
                found_non_zero = true;
                out.push_back(*it);
            }
        }
        std::reverse(out.begin(), out.end());
        return out;
    }

    std::vector<std::int64_t> VersionNumber::padded_version(size_t len) const {
        std::vector<std::int64_t> out(len);
        for (size_t i = 0; i < len; i++){
            out[i] = (*this)[i];
        }
        return out;
    }


    PlatformVersionContainer::PlatformVersionContainer(
        const PlatformType& platform,
        const VersionNumber& version
    ): platform(platform), version(version) {}

    void PlatformVersionContainer::serialise(Amulet::BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeSizeAndBytes(platform);
        version.serialise(writer);
    }
    PlatformVersionContainer PlatformVersionContainer::deserialise(Amulet::BinaryReader& reader){
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::string platform = reader.readSizeAndBytes();
            VersionNumber version = VersionNumber::deserialise(reader);
            return PlatformVersionContainer(platform, version);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }


    VersionRange::VersionRange(
        const PlatformType& platform,
        const VersionNumber& min_version,
        const VersionNumber& max_version
    ): platform(platform), min_version(min_version), max_version(max_version) {
        if (min_version > max_version){
            throw std::invalid_argument("min_version must be less than or equal to max_version");
        }
    }

    void VersionRange::serialise(Amulet::BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeSizeAndBytes(platform);
        min_version.serialise(writer);
        max_version.serialise(writer);
    }
    VersionRange VersionRange::deserialise(Amulet::BinaryReader& reader) {
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::string platform = reader.readSizeAndBytes();
            VersionNumber min_version = VersionNumber::deserialise(reader);
            VersionNumber max_version = VersionNumber::deserialise(reader);
            return VersionRange(platform, min_version, max_version);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }

    bool VersionRange::contains(const PlatformType& platform_, const VersionNumber& version) const {
        return platform == platform_ && min_version <= version && version <= max_version;
    }


    VersionRangeContainer::VersionRangeContainer(
        const VersionRange& version_range
    ): version_range(version_range) {}

    void VersionRangeContainer::serialise(Amulet::BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        version_range.serialise(writer);
    }
    VersionRangeContainer VersionRangeContainer::deserialise(Amulet::BinaryReader& reader) {
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            VersionRange version_range = VersionRange::deserialise(reader);
            return VersionRangeContainer(version_range);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }
}
