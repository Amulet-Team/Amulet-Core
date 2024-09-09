#include <map>
#include <variant>
#include <type_traits>
#include <string>
#include <functional>
#include <stdexcept>

#include <amulet/block.hpp>
#include <amulet_nbt/nbt_encoding/binary.hpp>
#include <amulet_nbt/nbt_encoding/string.hpp>

namespace Amulet {
    void Block::serialise(BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeSizeAndBytes(get_platform());
        get_version()->serialise(writer);
        writer.writeSizeAndBytes(namespace_);
        writer.writeSizeAndBytes(base_name);
        
        writer.writeNumeric<std::uint64_t>(properties.size());
        for (auto const& [key, val] : properties) {
            writer.writeSizeAndBytes(key);
            std::visit([&writer](auto&& tag) {
                AmuletNBT::write_nbt(writer, "", tag);
            }, val);
        }
    }
    std::shared_ptr<Block> Block::deserialise(BinaryReader& reader){
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::string platform = reader.readSizeAndBytes();
            std::shared_ptr<VersionNumber> version = VersionNumber::deserialise(reader);
            std::string namespace_ = reader.readSizeAndBytes();
            std::string base_name = reader.readSizeAndBytes();
            std::uint64_t property_count;
            BlockProperites properties;
            reader.readNumericInto<std::uint64_t>(property_count);
            for (std::uint64_t i = 0; i < property_count; i++) {
                std::string name = reader.readSizeAndBytes();
                AmuletNBT::NamedTag named_tag = AmuletNBT::read_nbt(reader);
                properties[name] = std::visit([](auto&& tag) -> PropertyValueType {
                    using T = std::decay_t<decltype(tag)>;
                    if constexpr (
                        std::is_same_v<T, AmuletNBT::ByteTag> ||
                        std::is_same_v<T, AmuletNBT::ShortTag> ||
                        std::is_same_v<T, AmuletNBT::IntTag> ||
                        std::is_same_v<T, AmuletNBT::LongTag> ||
                        std::is_same_v<T, AmuletNBT::StringTag>
                    ) {
                        return tag;
                    }
                    else {
                        throw std::invalid_argument("Property tag must be Byte, Short, Int, Long or String");
                    }
                }, named_tag.tag_node);
            }
            return std::make_shared<Block>(platform, version, namespace_, base_name, properties);
        }
        default:
            throw std::invalid_argument("Unsupported Block version " + std::to_string(version_number));
        }
    }

    template <typename T>
    inline std::vector<std::string> get_ordered_keys(const T& map) {
        std::vector<std::string> keys;
        keys.reserve(map.size());
        for (const auto& [key, _] : map) {
            keys.push_back(key);
        }
        std::sort(keys.begin(), keys.end());
        return keys;
    }

    std::string Block::java_blockstate() const {
        std::string blockstate;
        blockstate += get_namespace();
        blockstate += ":";
        blockstate += get_base_name();
        const auto& properties = get_properties();
        if (!properties.empty()) {
            blockstate += "[";
            auto keys = get_ordered_keys(properties);
            bool is_first = true;
            for (const std::string& key : keys) {
                const auto& it = properties.find(key);
                std::visit(
                    [&is_first, &blockstate, &key](auto&& tag) {
                        using T = std::decay_t<decltype(tag)>;
                        if constexpr (std::is_same_v<T, AmuletNBT::StringTag>) {
                            if (is_first) {
                                is_first = false;
                            }
                            else {
                                blockstate += ",";
                            }
                            blockstate += key;
                            blockstate += "=";
                            blockstate += tag;
                        }
                    },
                    it->second
                );
            }
            blockstate += "]";
        }
        return blockstate;
    }
    std::string Block::bedrock_blockstate() const {
        std::string blockstate;
        blockstate += get_namespace();
        blockstate += ":";
        blockstate += get_base_name();
        const auto& properties = get_properties();
        if (!properties.empty()) {
            blockstate += "[";
            auto keys = get_ordered_keys(properties);
            bool is_first = true;
            for (const std::string& key : keys) {
                const auto& it = properties.find(key);
                std::visit(
                    [&is_first, &blockstate, &key](auto&& tag) {
                        if (is_first) {
                            is_first = false;
                        }
                        else {
                            blockstate += ",";
                        }
                        blockstate += "\"";
                        blockstate += key;
                        blockstate += "\"=";
                        using T = std::decay_t<decltype(tag)>;
                        if constexpr (std::is_same_v<T, AmuletNBT::ByteTag>) {
                            if (tag == 0) {
                                blockstate += "false";
                            } else if (tag == 1) {
                                blockstate += "true";
                            }
                            else {
                                blockstate += AmuletNBT::write_snbt(tag);
                            }
                        }
                        else if constexpr (std::is_same_v<T, AmuletNBT::StringTag>) {
                            blockstate += "\"";
                            blockstate += tag;
                            blockstate += "\"";
                        }
                        else {
                            blockstate += AmuletNBT::write_snbt(tag);
                        }
                    },
                    it->second
                );
            }
            blockstate += "]";
        }
        return blockstate;
    }

    template <
        void(*namespace_validator)(const size_t&, const std::string&),
        void(*base_name_validator)(const size_t&, const std::string&),
        std::string(*capture_key)(const std::string&, size_t&),
        PropertyValueType(*capture_value)(const std::string&, size_t&)
    >
    std::shared_ptr<Block> parse_blockstate(
        const PlatformType& platform,
        std::shared_ptr<VersionNumber> version,
        const std::string& blockstate
    ) {
        // This is more lenient than the game parser.
        // It may parse formats that the game parsers wouldn't parse but it should support everything they do parse.
        
        // Find the start of the property section and the end of the resource identifier.
        size_t property_start = blockstate.find("[");
        if (property_start > blockstate.size()) {
            property_start = blockstate.size();
        }

        size_t colon_pos = blockstate.find(":");
        std::string namespace_;
        std::string base_name;
        if (colon_pos < property_start) {
            // namespaced name
            if (colon_pos == 0) { throw std::invalid_argument("namespace is empty"); }
            namespace_ = std::string(blockstate.begin(), blockstate.begin() + colon_pos);
            if (colon_pos + 1 == property_start) { throw std::invalid_argument("base name is empty"); }
            base_name = std::string(blockstate.begin() + colon_pos + 1, blockstate.begin() + property_start);
            namespace_validator(0, namespace_);
            base_name_validator(colon_pos + 1, base_name);
        }
        else {
            // only base name
            namespace_ = "minecraft";
            if (property_start == 0) { throw std::invalid_argument("base name is empty"); }
            base_name = std::string(blockstate.begin(), blockstate.begin() + property_start);
            base_name_validator(0, base_name);
        }

        if (property_start < blockstate.size()) {
            // has properties
            BlockProperites properties;
            size_t property_pos = property_start + 1;
            if (property_pos < blockstate.size() && blockstate[property_pos] == ']') {
                // []
                property_pos++;
                if (property_pos < blockstate.size()) {
                    throw std::invalid_argument("Extra data after ]");
                }
                return std::make_shared<Block>(platform, version, namespace_, base_name, properties);
            }
            for (;;) {
                std::string key = capture_key(blockstate, property_pos);

                if (property_pos >= blockstate.size() || blockstate[property_pos] != '=') {
                    throw std::invalid_argument("Expected = at position " + std::to_string(property_pos));
                }
                property_pos++;

                properties[key] = capture_value(blockstate, property_pos);

                if (property_pos >= blockstate.size()) {
                    throw std::invalid_argument("Expected , or ] at position " + std::to_string(property_pos));
                }
                switch (blockstate[property_pos]) {
                    case ',':
                        break;
                    case ']':
                        property_pos++;
                        if (property_pos < blockstate.size()) {
                            throw std::invalid_argument("Extra data after ]");
                        }
                        return std::make_shared<Block>(platform, version, namespace_, base_name, properties);
                    default:
                        throw std::invalid_argument("Expected , or ] at position " + std::to_string(property_pos));
                }
                property_pos++;
            }
        }
        else {
            // does not have properties
            return std::make_shared<Block>(platform, version, namespace_, base_name);
        }
    }

    auto is_alnum = [](const char& chr) {
        return (
            ('0' <= chr && chr <= '9') ||
            ('a' <= (chr | 32) && (chr | 32) <= 'z')
        );
    };
    
    inline void validate_java_namespace(const size_t& offset, const std::string& namespace_) {
        for (size_t i = 0; i < namespace_.size(); i++) {
            const auto& chr = namespace_[i];
            if (!(is_alnum(chr) || chr == '_' || chr == '-' || chr == '.')){
                throw std::invalid_argument("Invalid namespace character at position " + std::to_string(offset + i));
            }
        }
    }
    inline void validate_java_base_name(const size_t& offset, const std::string& base_name) {
        for (size_t i = 0; i < base_name.size(); i++) {
            const auto& chr = base_name[i];
            if (!(is_alnum(chr) || chr == '_' || chr == '-' || chr == '.' || chr == '/')) {
                throw std::invalid_argument("Invalid base name character at position " + std::to_string(offset + i));
            }
        }
    }
    // key=str
    inline std::string capture_java_blockstate_property_key(const std::string& blockstate, size_t& offset) {
        size_t key_start = offset;
        while (offset < blockstate.size()) {
            const auto& chr = blockstate[offset];
            if (!(is_alnum(chr) || chr == '_')) {
                break;
            }
            offset++;
        }
        if (key_start == offset) {
            throw std::invalid_argument("Expected a key or ] at position " + std::to_string(offset));
        }
        return std::string(blockstate.begin() + key_start, blockstate.begin() + offset);
    }
    inline PropertyValueType capture_java_blockstate_property_value(const std::string& blockstate, size_t& offset) {
        size_t value_start = offset;
        while (offset < blockstate.size()) {
            const auto& chr = blockstate[offset];
            if (!(is_alnum(chr) || chr == '_')) {
                break;
            }
            offset++;
        }
        if (value_start == offset) {
            throw std::invalid_argument("Expected a value at position " + std::to_string(offset));
        }
        return AmuletNBT::StringTag(blockstate.begin() + value_start, blockstate.begin() + offset);
    }

    // I think Bedrock resource identifiers are not limited to a-z0-9_-.
    inline void validate_bedrock_namespace(const size_t& offset, const std::string& namespace_) {
        for (size_t i = 0; i < namespace_.size(); i++) {
            const auto& chr = namespace_[i];
            if (!(is_alnum(chr) || chr == '_' || chr == '-' || chr == '.')) {
                throw std::invalid_argument("Invalid namespace character at position " + std::to_string(offset + i));
            }
        }
    }
    inline void validate_bedrock_base_name(const size_t& offset, const std::string& base_name) {
        for (size_t i = 0; i < base_name.size(); i++) {
            const auto& chr = base_name[i];
            if (!(is_alnum(chr) || chr == '_' || chr == '-' || chr == '.')) {
                throw std::invalid_argument("Invalid base name character at position " + std::to_string(offset + i));
            }
        }
    }
    // "key"=false
    // "key"=true
    // "key"=nbt
    inline std::string capture_bedrock_blockstate_property_key(const std::string& blockstate, size_t& offset) {
        // Opening "
        if (offset >= blockstate.size() || blockstate[offset] != '"') {
            throw std::invalid_argument("Expected \" at position " + std::to_string(offset));
        }
        offset++;

        // Key
        size_t key_start = offset;
        while (offset < blockstate.size()) {
            const auto& chr = blockstate[offset];
            if (!(is_alnum(chr) || chr == '_')) {
                break;
            }
            offset++;
        }
        if (key_start == offset) {
            throw std::invalid_argument("Expected a key or ] at position " + std::to_string(offset));
        }
        size_t key_end = offset;

        // Closing "
        if (offset >= blockstate.size() || blockstate[offset] != '"') {
            throw std::invalid_argument("Expected \" at position " + std::to_string(offset));
        }
        offset++;

        return std::string(blockstate.begin() + key_start, blockstate.begin() + key_end);
    }
    inline PropertyValueType capture_bedrock_blockstate_property_value(const std::string& blockstate, size_t& offset) {
        size_t value_start = offset;
        size_t value_end = std::min(
            blockstate.find(",", value_start),
            blockstate.find("]", value_start)
        );
        if (value_end >= blockstate.size()) {
            throw std::invalid_argument("Expected , or ] after position " + std::to_string(offset));
        }
        offset = value_end;
        AmuletNBT::TagNode node;
        try {
            node = AmuletNBT::read_snbt(std::string(blockstate.begin() + value_start, blockstate.begin() + value_end));
        }
        catch (const std::exception& e) {
            throw std::invalid_argument("Failed parsing SNBT at position " + std::to_string(value_start) + ". " + e.what());
        }
        return std::visit(
            [](auto&& tag) -> PropertyValueType {
                using T = std::decay_t<decltype(tag)>;
                if constexpr (
                    std::is_same_v<T, AmuletNBT::ByteTag> ||
                    std::is_same_v<T, AmuletNBT::ShortTag> ||
                    std::is_same_v<T, AmuletNBT::IntTag> ||
                    std::is_same_v<T, AmuletNBT::LongTag> ||
                    std::is_same_v<T, AmuletNBT::StringTag>
                ) {
                    return tag;
                }
                else {
                    throw std::invalid_argument("Values must be byte, short, int, long or string tags.");
                }
            },
            node
        );
    }

    std::shared_ptr<Block> Block::from_java_blockstate(const PlatformType& platform, std::shared_ptr<VersionNumber> version, const std::string& blockstate) {
        return parse_blockstate<
            validate_java_namespace,
            validate_java_base_name,
            capture_java_blockstate_property_key,
            capture_java_blockstate_property_value
        >(
            platform, 
            version, 
            blockstate
        );
    }
    std::shared_ptr<Block> Block::from_bedrock_blockstate(const PlatformType& platform, std::shared_ptr<VersionNumber> version, const std::string& blockstate) {
        return parse_blockstate<
            validate_bedrock_namespace,
            validate_bedrock_base_name,
            capture_bedrock_blockstate_property_key,
            capture_bedrock_blockstate_property_value
        >(
            platform, 
            version, 
            blockstate
        );
    }

    void BlockStack::serialise(BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeNumeric<std::uint64_t>(get_blocks().size());
        for (const auto& block : get_blocks()) {
            block->serialise(writer);
        }
    }
    std::shared_ptr<BlockStack> BlockStack::deserialise(BinaryReader& reader) {
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::vector<std::shared_ptr<Block>> blocks;
            auto count = reader.readNumeric<std::uint64_t>();
            for (auto i = 0; i < count; i++) {
                blocks.push_back(Block::deserialise(reader));
            }
            return std::make_shared<BlockStack>(blocks);
        }
        default:
            throw std::invalid_argument("Unsupported BlockStack version " + std::to_string(version_number));
        }
    }
}
