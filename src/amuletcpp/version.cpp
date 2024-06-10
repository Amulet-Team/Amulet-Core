#include <stdexcept>
#include <amuletcpp/version.hpp>


namespace Amulet {
    VersionNumber::VersionNumber(std::initializer_list<std::int64_t> value): value(value) {};
    VersionNumber::VersionNumber(std::vector<std::int64_t> value): value(value) {};

    // serialise
    // deserialise

    std::vector<std::int64_t>::const_iterator VersionNumber::begin() const {
        return value.begin();
    }

    std::vector<std::int64_t>::const_iterator VersionNumber::end() const {
        return value.end();
    }

    std::vector<std::int64_t>::const_reverse_iterator VersionNumber::rbegin() const {
        return value.rbegin();
    }

    std::vector<std::int64_t>::const_reverse_iterator VersionNumber::rend() const {
        return value.rend();
    }

    size_t VersionNumber::size() const {
        return value.size();
    }

    std::int64_t VersionNumber::operator[](size_t index) const {
        if (index >= value.size()) {
            return 0;
        }
        return value[index];
    }

    bool VersionNumber::operator==(const VersionNumber& other) const {
        size_t max_len = std::max(value.size(), other.size());
        for (size_t i = 0; i < max_len; i++){
            if ((*this)[i] != other[i]){
                return false;
            }
        }
        return true;
    }

    bool VersionNumber::operator!=(const VersionNumber& other) const {
        return !(*this == other);
    }

    bool VersionNumber::operator<(const VersionNumber& other) const {
        size_t max_len = std::max(value.size(), other.size());
        std::int64_t v1, v2;
        for (size_t i = 0; i < max_len; i++){
            v1 = (*this)[i];
            v2 = other[i];
            if (v1 < v2){
                // Less than
                return true;
            }
            if (v1 > v2){
                // Greater than
                return false;
            }
        }
        // equal
        return false;
    }

    bool VersionNumber::operator>(const VersionNumber& other) const {
        return other < *this;
    }

    bool VersionNumber::operator<=(const VersionNumber& other) const {
        return !(*this > other);
    }

    bool VersionNumber::operator>=(const VersionNumber& other) const {
        return !(*this < other);
    }

    std::string VersionNumber::toString() const {
        std::ostringstream oss;
        for (size_t i = 0; i < value.size(); ++i) {
            if (i > 0){
                oss << '.';
            }
            oss << value[i];
        }
        return oss.str();
    }

    std::string VersionNumber::repr() const {
        std::ostringstream oss;
        oss << "VersionNumber(";
        for (size_t i = 0; i < value.size(); ++i) {
            if (i > 0){
                oss << ", ";
            }
            oss << value[i];
        }
        oss << ")";
        return oss.str();
    }

    std::vector<std::int64_t> VersionNumber::cropped_version() const {
        bool found_non_zero = false;
        std::vector<std::int64_t> out;
        for (auto it = value.rbegin(); it != value.rend(); ++it) {
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

    std::string PlatformVersionContainer::repr() const {
        return "PlatformVersionContainer(" + platform + ", " + version.repr() + ")";
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

    std::string VersionRange::repr() const {
        return "VersionRange(" + platform + ", " + min_version.repr() + ", " + max_version.repr() + ")";
    }

    bool VersionRange::contains(const PlatformType& platform_, const VersionNumber& version) const {
        return platform == platform_ && min_version <= version && version <= max_version;
    }


    VersionRangeContainer::VersionRangeContainer(
        const VersionRange& version_range
    ): version_range(version_range) {}

    std::string VersionRangeContainer::repr() const {
        return "VersionRangeContainer(" + version_range.repr() + ")";
    }
}
