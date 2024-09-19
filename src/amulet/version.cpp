#include <stdexcept>
#include <cstdint>
#include <compare>

#include <amulet/version.hpp>


namespace Amulet {
    void VersionNumber::serialise(BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeNumeric<std::uint64_t>(vec.size());
        for (const std::int64_t& v : vec){
            writer.writeNumeric<std::int64_t>(v);
        }
    }
    std::shared_ptr<VersionNumber> VersionNumber::deserialise(BinaryReader& reader){
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
                return std::make_shared<VersionNumber>(vec);
            }
            default:
                throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
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

    void PlatformVersionContainer::serialise(BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeSizeAndBytes(platform);
        version->serialise(writer);
    }
    std::shared_ptr<PlatformVersionContainer> PlatformVersionContainer::deserialise(BinaryReader& reader){
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::string platform = reader.readSizeAndBytes();
            auto version = VersionNumber::deserialise(reader);
            return std::make_shared<PlatformVersionContainer>(platform, version);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }

    void VersionRange::serialise(BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeSizeAndBytes(platform);
        min_version->serialise(writer);
        max_version->serialise(writer);
    }
    std::shared_ptr<VersionRange> VersionRange::deserialise(BinaryReader& reader) {
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::string platform = reader.readSizeAndBytes();
            auto min_version = VersionNumber::deserialise(reader);
            auto max_version = VersionNumber::deserialise(reader);
            return std::make_shared<VersionRange>(platform, min_version, max_version);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }

    bool VersionRange::contains(const PlatformType& platform_, const VersionNumber& version) const {
        return platform == platform_ && *min_version <= version && version <= *max_version;
    }

    void VersionRangeContainer::serialise(BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        version_range->serialise(writer);
    }
    std::shared_ptr<VersionRangeContainer> VersionRangeContainer::deserialise(BinaryReader& reader) {
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            return std::make_shared<VersionRangeContainer>(
                VersionRange::deserialise(reader)
            );
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }
}
