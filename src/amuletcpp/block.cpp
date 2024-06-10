#include <amuletcpp/block.hpp>

namespace Amulet {
    Block::Block(
        const PlatformType& platform,
        const VersionNumber& version,
        const std::string& namespace_,
        const std::string& base_name
    ) : PlatformVersionContainer(platform, version), namespace_(namespace_), base_name(base_name) {}

    std::string Block::repr() const {
        return "Block(" + platform + ", " + version.repr() + ", " + namespace_ + ", " + base_name + ")";
    }
}
