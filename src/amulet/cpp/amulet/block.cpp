#include <amulet/block.hpp>

namespace Amulet {
    Block::Block(
        const PlatformType& platform,
        const VersionNumber& version,
        const std::string& namespace_,
        const std::string& base_name
    ) : PlatformVersionContainer(platform, version), namespace_(namespace_), base_name(base_name) {}
}
