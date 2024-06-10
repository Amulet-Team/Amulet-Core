#include <amuletcpp/version.hpp>


namespace Amulet {
    class Block: public PlatformVersionContainer {
        public:
            const std::string namespace_;
            const std::string base_name;

            Block(
                const PlatformType&,
                const VersionNumber&,
                const std::string&,
                const std::string&
            );

            std::string repr() const;
    };
}
