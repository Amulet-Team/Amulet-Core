#pragma once

#include <map>
#include <variant>
#include <string>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>
#include <amulet/version.hpp>
#include <amulet_nbt/tag/named_tag.hpp>
#include <amulet_nbt/tag/eq.hpp>


namespace Amulet {
    class BlockEntity: public PlatformVersionContainer {
        private:
            std::string _namespace;
            std::string _base_name;
            std::shared_ptr<AmuletNBT::NamedTag> _nbt;
            
        public:
            const std::string& get_namespace() const { return _namespace; }
            void set_namespace(const std::string& namespace_) { _namespace = namespace_; }
            
            const std::string& get_base_name() const { return _base_name; }
            void set_base_name(const std::string& base_name) { _base_name = base_name; }
            
            std::shared_ptr<AmuletNBT::NamedTag> get_nbt() const { return _nbt; }
            void set_nbt(std::shared_ptr<AmuletNBT::NamedTag> nbt) { _nbt = nbt; }

            BlockEntity(
                const PlatformType& platform,
                std::shared_ptr<VersionNumber> version,
                const std::string& namespace_,
                const std::string& base_name,
                std::shared_ptr<AmuletNBT::NamedTag> nbt
            ):
                PlatformVersionContainer(platform, version),
                _namespace(namespace_),
                _base_name(base_name),
                _nbt(nbt)
            {}

            void serialise(BinaryWriter&) const;
            static std::shared_ptr<BlockEntity> deserialise(BinaryReader&);

            bool operator==(const BlockEntity& other) const {
                return (
                    PlatformVersionContainer::operator==(other) &&
                    _namespace == other._namespace &&
                    _base_name == other._base_name &&
                    AmuletNBT::NBTTag_eq(*_nbt, *other._nbt)
                );
            };
    };
}
