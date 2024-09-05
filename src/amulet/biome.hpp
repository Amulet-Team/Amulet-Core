#pragma once

#include <string>

#include <amulet/version.hpp>
#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>


namespace Amulet {
    class Biome: public PlatformVersionContainer {
        private:
            std::string namespace_;
            std::string base_name;
        public:
            const std::string& get_namespace() const { return namespace_; }
            const std::string& get_base_name() const { return base_name; }

            Biome(
                const PlatformType& platform,
                std::shared_ptr<VersionNumber> version,
                const std::string& namespace_,
                const std::string& base_name
            ):
                PlatformVersionContainer(platform, version),
                namespace_(namespace_),
                base_name(base_name) {}

            void serialise(BinaryWriter&) const;
            static std::shared_ptr<Biome> deserialise(BinaryReader&);

            auto operator<=>(const Biome& other) const {
                auto cmp = PlatformVersionContainer::operator<=>(other);
                if (cmp != 0) { return cmp; }
                cmp = namespace_ <=> other.namespace_;
                if (cmp != 0) { return cmp; }
                return base_name <=> other.base_name;
            }
            bool operator==(const Biome& other) const {
                return (*this <=> other) == 0;
            };
    };
}
