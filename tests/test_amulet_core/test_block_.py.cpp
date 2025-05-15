#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <functional>
#include <list>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/nbt/tag/int.hpp>

#include <amulet/test_utils/test_utils.hpp>

#include <amulet/core/block/block.hpp>
#include <amulet/core/version/version.hpp>

namespace py = pybind11;

static const Amulet::VersionNumber VersionTuple { 1, 2, 3 };

static void test_block_ctor_attrs_lvalue()
{
    Amulet::PlatformType block_platform = "java";
    Amulet::VersionNumber block_version = { 1, 2, 3 };
    std::string block_namespace = "hello";
    std::string block_base_name = "world";
    Amulet::Block::PropertyMap block_properties { { "key", Amulet::NBT::IntTag(5) } };

    Amulet::Block block_lvalue_1(block_platform, block_version, block_namespace, block_base_name);

    ASSERT_EQUAL(std::string, "java", block_lvalue_1.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, block_lvalue_1.get_version());
    ASSERT_EQUAL(std::string, "hello", block_lvalue_1.get_namespace());
    ASSERT_EQUAL(std::string, "world", block_lvalue_1.get_base_name());
    ASSERT_EQUAL(Amulet::Block::PropertyMap, {}, block_lvalue_1.get_properties());

    Amulet::Block block_lvalue_2(block_platform, block_version, block_namespace, block_base_name, block_properties);

    ASSERT_EQUAL(std::string, "java", block_lvalue_2.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, block_lvalue_2.get_version());
    ASSERT_EQUAL(std::string, "hello", block_lvalue_2.get_namespace());
    ASSERT_EQUAL(std::string, "world", block_lvalue_2.get_base_name());
    ASSERT_EQUAL(Amulet::Block::PropertyMap, block_properties, block_lvalue_2.get_properties());
}

static void test_block_ctor_attrs_rvalue()
{
    Amulet::Block block_rvalue_1("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");

    ASSERT_EQUAL(std::string, "java", block_rvalue_1.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, block_rvalue_1.get_version());
    ASSERT_EQUAL(std::string, "hello", block_rvalue_1.get_namespace());
    ASSERT_EQUAL(std::string, "world", block_rvalue_1.get_base_name());
    ASSERT_EQUAL(Amulet::Block::PropertyMap, {}, block_rvalue_1.get_properties());

    Amulet::Block::PropertyMap block_properties_ { { "key", Amulet::NBT::IntTag(5) } };
    Amulet::Block block_rvalue_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", std::move(block_properties_));

    ASSERT_EQUAL(std::string, "java", block_rvalue_2.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, block_rvalue_2.get_version());
    ASSERT_EQUAL(std::string, "hello", block_rvalue_2.get_namespace());
    ASSERT_EQUAL(std::string, "world", block_rvalue_2.get_base_name());
    Amulet::Block::PropertyMap block_properties { { "key", Amulet::NBT::IntTag(5) } };
    ASSERT_EQUAL(Amulet::Block::PropertyMap, block_properties, block_rvalue_2.get_properties());
}

static void test_block_ctor_attrs_view()
{
    Amulet::PlatformType block_platform = "java";
    Amulet::VersionNumber block_version = { 1, 2, 3 };
    std::string block_namespace = "hello";
    std::string block_base_name = "world";

    std::string_view block_platform_view = block_platform;
    std::string_view block_namespace_view = block_namespace;
    std::string_view block_base_name_view = block_base_name;

    Amulet::Block block_lvalue_1(block_platform_view, block_version, block_namespace_view, block_base_name_view);

    ASSERT_EQUAL(std::string, "java", block_lvalue_1.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, block_lvalue_1.get_version());
    ASSERT_EQUAL(std::string, "hello", block_lvalue_1.get_namespace());
    ASSERT_EQUAL(std::string, "world", block_lvalue_1.get_base_name());
    ASSERT_EQUAL(Amulet::Block::PropertyMap, {}, block_lvalue_1.get_properties());

    Amulet::Block::PropertyMap block_properties { { "key", Amulet::NBT::IntTag(5) } };
    Amulet::Block block_lvalue_2(block_platform_view, block_version, block_namespace_view, block_base_name_view, block_properties);

    ASSERT_EQUAL(std::string, "java", block_lvalue_2.get_platform());
    ASSERT_EQUAL(Amulet::VersionNumber, VersionTuple, block_lvalue_2.get_version());
    ASSERT_EQUAL(std::string, "hello", block_lvalue_2.get_namespace());
    ASSERT_EQUAL(std::string, "world", block_lvalue_2.get_base_name());
    ASSERT_EQUAL(Amulet::Block::PropertyMap, block_properties, block_lvalue_2.get_properties());
}

static void test_block_equal()
{
    Amulet::Block::PropertyMap empty_block_properties;
    Amulet::Block::PropertyMap block_properties { { "key", Amulet::NBT::IntTag(5) } };

    Amulet::Block block_1("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Block block_1a("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Block block_1b("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", empty_block_properties);
    Amulet::Block block_2("java_", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Block block_3("java", Amulet::VersionNumber { 0, 2, 3 }, "hello", "world");
    Amulet::Block block_4("java", Amulet::VersionNumber { 1, 3, 3 }, "hello", "world");
    Amulet::Block block_5("java", Amulet::VersionNumber { 1, 2, 4 }, "hello", "world");
    Amulet::Block block_6("java", Amulet::VersionNumber { 1, 2, 3 }, "hello_", "world");
    Amulet::Block block_7("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world_");
    Amulet::Block block_8("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", block_properties);
    ASSERT_EQUAL(Amulet::Block, block_1, block_1a);
    ASSERT_EQUAL(Amulet::Block, block_1, block_1b);
    ASSERT_NOT_EQUAL(Amulet::Block, block_1, block_2);
    ASSERT_NOT_EQUAL(Amulet::Block, block_1, block_3);
    ASSERT_NOT_EQUAL(Amulet::Block, block_1, block_4);
    ASSERT_NOT_EQUAL(Amulet::Block, block_1, block_5);
    ASSERT_NOT_EQUAL(Amulet::Block, block_1, block_6);
    ASSERT_NOT_EQUAL(Amulet::Block, block_1, block_7);
    ASSERT_NOT_EQUAL(Amulet::Block, block_1, block_8);
}

static void test_block_compare()
{
    Amulet::Block::PropertyMap empty_block_properties;
    Amulet::Block::PropertyMap block_properties { { "key", Amulet::NBT::IntTag(5) } };

    Amulet::Block block_1("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Block block_1a("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Block block_1b("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", empty_block_properties);
    Amulet::Block block_2("java_", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    Amulet::Block block_3("java", Amulet::VersionNumber { 0, 2, 3 }, "hello", "world");
    Amulet::Block block_4("java", Amulet::VersionNumber { 1, 3, 3 }, "hello", "world");
    Amulet::Block block_5("java", Amulet::VersionNumber { 1, 2, 4 }, "hello", "world");
    Amulet::Block block_6("java", Amulet::VersionNumber { 1, 2, 3 }, "hello_", "world");
    Amulet::Block block_7("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world_");
    Amulet::Block block_8("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", block_properties);

    ASSERT_EQUAL(Amulet::Block, block_1, block_1a);
    ASSERT_GREATER_EQUAL(Amulet::Block, block_1, block_1a);
    ASSERT_LESS_EQUAL(Amulet::Block, block_1, block_1a);

    ASSERT_LESS(Amulet::Block, block_1, block_2);
    ASSERT_GREATER(Amulet::Block, block_1, block_3);
    ASSERT_LESS(Amulet::Block, block_1, block_4);
    ASSERT_LESS(Amulet::Block, block_1, block_5);
    ASSERT_LESS(Amulet::Block, block_1, block_6);
    ASSERT_LESS(Amulet::Block, block_1, block_7);
    ASSERT_LESS(Amulet::Block, block_1, block_8);
}

static void test_block_serialise()
{
    std::string encoded_base("\x01\x04\x00\x00\x00\x00\x00\x00\x00java\x01\x03\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00hello\x05\x00\x00\x00\x00\x00\x00\x00world", 72);

    Amulet::Block block_1("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
    std::string encoded_1 = encoded_base + std::string("\x00\x00\x00\x00\x00\x00\x00\x00", 8);

    ASSERT_EQUAL(std::string, encoded_1, Amulet::serialise(block_1))
    ASSERT_EQUAL(Amulet::Block, block_1, Amulet::deserialise<Amulet::Block>(encoded_1))

    Amulet::Block::PropertyMap empty_block_properties;
    Amulet::Block block_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", empty_block_properties);
    std::string encoded_2 = encoded_base + std::string("\x00\x00\x00\x00\x00\x00\x00\x00", 8);

    ASSERT_EQUAL(std::string, encoded_2, Amulet::serialise(block_2))
    ASSERT_EQUAL(Amulet::Block, block_2, Amulet::deserialise<Amulet::Block>(encoded_2))

    Amulet::Block::PropertyMap block_properties { { "key", Amulet::NBT::IntTag(5) } };
    Amulet::Block block_3("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", block_properties);
    std::string encoded_3 = encoded_base + std::string("\x01\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00key\x03\x05\x00\x00\x00", 24);

    ASSERT_EQUAL(std::string, encoded_3, Amulet::serialise(block_3))
    ASSERT_EQUAL(Amulet::Block, block_3, Amulet::deserialise<Amulet::Block>(encoded_3))
}

static void test_java_blockstate()
{
    Amulet::Block::PropertyMap empty_block_properties;
    {
        // default namespace
        Amulet::Block block("java", Amulet::VersionNumber { 1, 2, 3 }, "minecraft", "hello_world", empty_block_properties);
        ASSERT_EQUAL(Amulet::Block, block, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello_world"))
    }
    {
        // block with default empty properties
        Amulet::Block block("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        ASSERT_EQUAL(std::string, "hello:world", block.java_blockstate())
        ASSERT_EQUAL(Amulet::Block, block, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world"))
        ASSERT_EQUAL(Amulet::Block, block, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[]"))
    }
    {
        // block with empty properties
        Amulet::Block block("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", empty_block_properties);
        ASSERT_EQUAL(std::string, "hello:world", block.java_blockstate())
    }
    {
        // non-string properties
        Amulet::Block::PropertyMap block_properties {
            { "byte_negative", Amulet::NBT::ByteTag(-5) },
            { "byte_false", Amulet::NBT::ByteTag(0) },
            { "byte_true", Amulet::NBT::ByteTag(1) },
            { "byte_positive", Amulet::NBT::ByteTag(5) },
            { "short_negative", Amulet::NBT::ShortTag(-5) },
            { "short_positive", Amulet::NBT::ShortTag(5) },
            { "int_negative", Amulet::NBT::IntTag(-5) },
            { "int_positive", Amulet::NBT::IntTag(5) },
            { "long_negative", Amulet::NBT::LongTag(-5) },
            { "long_positive", Amulet::NBT::LongTag(5) },
            { "string_2", Amulet::NBT::StringTag("hello_world") },
            { "string_1", Amulet::NBT::StringTag("hello_world") }
        };
        Amulet::Block block("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", block_properties);
        ASSERT_EQUAL(std::string, "hello:world[string_1=hello_world,string_2=hello_world]", block.java_blockstate())
    }
    {
        // parsing properties
        Amulet::Block::PropertyMap block_properties {
            { "string_2", Amulet::NBT::StringTag("hello_world") },
            { "string_1", Amulet::NBT::StringTag("hello_world") }
        };
        Amulet::Block block("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", block_properties);
        ASSERT_EQUAL(Amulet::Block, block, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[string_1=hello_world,string_2=hello_world]"))
    }
    {
        // test parsing errors
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, ":hello_world"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello_world:"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world["))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[abc"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[abc="))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[abc=hello"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[abc=hello]world"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_java_blockstate("java", Amulet::VersionNumber { 1, 2, 3 }, "hello:world]"))
    }
}

static void test_bedrock_blockstate()
{
    Amulet::Block::PropertyMap empty_block_properties;
    {
        // default namespace
        Amulet::Block block("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "minecraft", "hello_world", empty_block_properties);
        ASSERT_EQUAL(Amulet::Block, block, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello_world"))
    }
    {
        // block with default empty properties
        Amulet::Block block("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        ASSERT_EQUAL(std::string, "hello:world", block.bedrock_blockstate())
        ASSERT_EQUAL(Amulet::Block, block, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello:world"))
        ASSERT_EQUAL(Amulet::Block, block, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[]"))
    }
    {
        // block with empty properties
        Amulet::Block block("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", empty_block_properties);
        ASSERT_EQUAL(std::string, "hello:world", block.bedrock_blockstate())
    }
    {
        // non-string properties
        Amulet::Block::PropertyMap block_properties {
            { "byte_negative", Amulet::NBT::ByteTag(-5) },
            { "byte_false", Amulet::NBT::ByteTag(0) },
            { "byte_true", Amulet::NBT::ByteTag(1) },
            { "byte_positive", Amulet::NBT::ByteTag(5) },
            { "short_negative", Amulet::NBT::ShortTag(-5) },
            { "short_positive", Amulet::NBT::ShortTag(5) },
            { "int_negative", Amulet::NBT::IntTag(-5) },
            { "int_positive", Amulet::NBT::IntTag(5) },
            { "long_negative", Amulet::NBT::LongTag(-5) },
            { "long_positive", Amulet::NBT::LongTag(5) },
            { "string_2", Amulet::NBT::StringTag("hello_world") },
            { "string_1", Amulet::NBT::StringTag("hello_world") }
        };

        Amulet::Block block("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", block_properties);
        std::string block_state = "hello:world[\"byte_false\"=false,\"byte_negative\"=-5b,\"byte_positive\"=5b,\"byte_true\"=true,\"int_negative\"=-5,\"int_positive\"=5,\"long_negative\"=-5L,\"long_positive\"=5L,\"short_negative\"=-5s,\"short_positive\"=5s,\"string_1\"=\"hello_world\",\"string_2\"=\"hello_world\"]";
        ASSERT_EQUAL(std::string, block_state, block.bedrock_blockstate())
    }
    {
        // parsing properties
        Amulet::Block::PropertyMap block_properties {
            { "byte_negative", Amulet::NBT::ByteTag(-5) },
            { "byte_false", Amulet::NBT::ByteTag(0) },
            { "byte_true", Amulet::NBT::ByteTag(1) },
            { "byte_zero", Amulet::NBT::ByteTag(0) },
            { "byte_one", Amulet::NBT::ByteTag(1) },
            { "byte_positive", Amulet::NBT::ByteTag(5) },
            { "short_negative", Amulet::NBT::ShortTag(-5) },
            { "short_positive", Amulet::NBT::ShortTag(5) },
            { "int_negative", Amulet::NBT::IntTag(-5) },
            { "int_positive", Amulet::NBT::IntTag(5) },
            { "long_negative", Amulet::NBT::LongTag(-5) },
            { "long_positive", Amulet::NBT::LongTag(5) },
            { "string_2", Amulet::NBT::StringTag("hello_world") },
            { "string_1", Amulet::NBT::StringTag("hello_world") }
        };

        Amulet::Block block("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world", block_properties);
        std::string block_state = "hello:world[\"byte_false\"=false,\"byte_negative\"=-5b,\"byte_one\"=1b,\"byte_positive\"=5b,\"byte_true\"=true,\"byte_zero\"=0b,\"int_negative\"=-5,\"int_positive\"=5,\"long_negative\"=-5L,\"long_positive\"=5L,\"short_negative\"=-5s,\"short_positive\"=5s,\"string_1\"=\"hello_world\",\"string_2\"=\"hello_world\"]";
        ASSERT_EQUAL(Amulet::Block, block, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, block_state))
    }
    {
        // test parsing errors
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, ":hello_world"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello_world:"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello:world["))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[abc"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[abc="))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[abc=hello"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello:world[abc=hello]world"))
        ASSERT_RAISES(std::invalid_argument, Amulet::Block::from_bedrock_blockstate("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello:world]"))
    }
}

#define add_test(test_name) tests.push_back({ #test_name, test_name });

static std::vector<std::pair<std::string, std::function<void()>>> get_block_tests()
{
    std::vector<std::pair<std::string, std::function<void()>>> tests;

    add_test(test_block_ctor_attrs_lvalue);
    add_test(test_block_ctor_attrs_rvalue);
    add_test(test_block_ctor_attrs_view);
    add_test(test_block_equal);
    add_test(test_block_compare);
    add_test(test_block_serialise);
    add_test(test_java_blockstate);
    add_test(test_bedrock_blockstate);

    return tests;
}

static void test_block_stack_ctor_args_lvalue()
{
    {
        // initialiser list 1
        Amulet::Block block("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        Amulet::BlockStack block_stack({ block });
        ASSERT_EQUAL(size_t, 1, block_stack.size())
        ASSERT_EQUAL(Amulet::Block, block, block_stack.at(0))
        ASSERT_RAISES(std::out_of_range, block_stack.at(1))

        ASSERT_EQUAL(size_t, 1, block_stack.get_blocks().size())
        ASSERT_EQUAL(Amulet::Block, block, block_stack.get_blocks().at(0))
    }
    {
        // initialiser list 2
        Amulet::Block block_1("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        Amulet::Block block_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        Amulet::BlockStack block_stack({ block_1, block_2 });
        ASSERT_EQUAL(size_t, 2, block_stack.size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.at(1))
        ASSERT_RAISES(std::out_of_range, block_stack.at(2))

        ASSERT_EQUAL(size_t, 2, block_stack.get_blocks().size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.get_blocks().at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.get_blocks().at(1))
    }
    {
        // initialiser list 2 inline
        Amulet::BlockStack block_stack({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });

        Amulet::Block block_1("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        Amulet::Block block_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        ASSERT_EQUAL(size_t, 2, block_stack.size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.at(1))
        ASSERT_RAISES(std::out_of_range, block_stack.at(2))

        ASSERT_EQUAL(size_t, 2, block_stack.get_blocks().size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.get_blocks().at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.get_blocks().at(1))
    }
    {
        // vector
        Amulet::Block block_1("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        Amulet::Block block_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        std::vector<Amulet::Block> blocks { block_1, block_2 };
        Amulet::BlockStack block_stack(blocks);
        ASSERT_EQUAL(size_t, 2, block_stack.size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.at(1))
        ASSERT_RAISES(std::out_of_range, block_stack.at(2))

        ASSERT_EQUAL(size_t, 2, block_stack.get_blocks().size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.get_blocks().at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.get_blocks().at(1))
    }
    {
        // list iterators
        Amulet::Block block_1("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        Amulet::Block block_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        std::list<Amulet::Block> blocks { block_1, block_2 };
        Amulet::BlockStack block_stack(blocks.begin(), blocks.end());
        ASSERT_EQUAL(size_t, 2, block_stack.size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.at(1))
        ASSERT_RAISES(std::out_of_range, block_stack.at(2))

        ASSERT_EQUAL(size_t, 2, block_stack.get_blocks().size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.get_blocks().at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.get_blocks().at(1))
    }
}

static void test_block_stack_ctor_args_rvalue()
{
    {
        // vector
        Amulet::Block block_1("bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        Amulet::Block block_2("java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world");
        std::vector<Amulet::Block> blocks { block_1, block_2 };
        // Not good code. Used to make sure the vector is actually moved.
        const auto* vec_ptr = &blocks.at(0);
        Amulet::BlockStack block_stack(std::move(blocks));
        ASSERT_EQUAL(const Amulet::Block*, vec_ptr, &block_stack.at(0))
        ASSERT_EQUAL(size_t, 2, block_stack.size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.at(1))
        ASSERT_RAISES(std::out_of_range, block_stack.at(2))

        ASSERT_EQUAL(size_t, 2, block_stack.get_blocks().size())
        ASSERT_EQUAL(Amulet::Block, block_1, block_stack.get_blocks().at(0))
        ASSERT_EQUAL(Amulet::Block, block_2, block_stack.get_blocks().at(1))
    }
}

static void test_block_stack_ctor_errors()
{
    ASSERT_RAISES(std::invalid_argument, Amulet::BlockStack block_stack)
    ASSERT_RAISES(std::invalid_argument, Amulet::BlockStack block_stack({}))
}

static void test_block_stack_compare()
{
    {
        // size sort
        Amulet::BlockStack block_stack_1({
            { "z", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        Amulet::BlockStack block_stack_2({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        ASSERT_LESS(Amulet::BlockStack, block_stack_1, block_stack_2)
        ASSERT_GREATER(Amulet::BlockStack, block_stack_2, block_stack_1)
        ASSERT_NOT_EQUAL(Amulet::BlockStack, block_stack_1, block_stack_2)
    }
    {
        // value sort a
        Amulet::BlockStack block_stack_1({
            { "bedrock1", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        Amulet::BlockStack block_stack_2({
            { "bedrock2", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        ASSERT_LESS(Amulet::BlockStack, block_stack_1, block_stack_2)
        ASSERT_GREATER(Amulet::BlockStack, block_stack_2, block_stack_1)
        ASSERT_NOT_EQUAL(Amulet::BlockStack, block_stack_1, block_stack_2)
    }
    {
        // value sort b
        Amulet::BlockStack block_stack_1({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        Amulet::BlockStack block_stack_2({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world_" },
        });
        ASSERT_LESS(Amulet::BlockStack, block_stack_1, block_stack_2)
        ASSERT_GREATER(Amulet::BlockStack, block_stack_2, block_stack_1)
        ASSERT_NOT_EQUAL(Amulet::BlockStack, block_stack_1, block_stack_2)
    }
}

static void test_block_stack_equal()
{
    {
        // equal 1
        Amulet::BlockStack block_stack_1({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        Amulet::BlockStack block_stack_2({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        ASSERT_EQUAL(Amulet::BlockStack, block_stack_1, block_stack_2)
    }
    {
        // equal 2
        Amulet::BlockStack block_stack_1({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        Amulet::BlockStack block_stack_2({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        ASSERT_EQUAL(Amulet::BlockStack, block_stack_1, block_stack_2)
    }
    {
        // not equal
        Amulet::BlockStack block_stack_1({
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        Amulet::BlockStack block_stack_2({
            { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
            { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" },
        });
        ASSERT_NOT_EQUAL(Amulet::BlockStack, block_stack_1, block_stack_2)
    }
}

static void test_block_stack_serialisation()
{
    {
        Amulet::Block block { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" };
        Amulet::BlockStack block_stack({ block });
        std::string encoded = std::string("\x01\x01\x00\x00\x00\x00\x00\x00\x00", 9) + Amulet::serialise(block);
        ASSERT_EQUAL(std::string, encoded, Amulet::serialise(block_stack))
        ASSERT_EQUAL(Amulet::BlockStack, block_stack, Amulet::deserialise<Amulet::BlockStack>(encoded))
    }
    {
        Amulet::Block block_1 { "bedrock", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" };
        Amulet::Block block_2 { "java", Amulet::VersionNumber { 1, 2, 3 }, "hello", "world" };
        Amulet::BlockStack block_stack({ block_1, block_2 });
        std::string encoded = std::string("\x01\x02\x00\x00\x00\x00\x00\x00\x00", 9) + Amulet::serialise(block_1) + Amulet::serialise(block_2);
        ASSERT_EQUAL(std::string, encoded, Amulet::serialise(block_stack))
        ASSERT_EQUAL(Amulet::BlockStack, block_stack, Amulet::deserialise<Amulet::BlockStack>(encoded))
    }
}

static std::vector<std::pair<std::string, std::function<void()>>> get_block_stack_tests()
{
    std::vector<std::pair<std::string, std::function<void()>>> tests;

    add_test(test_block_stack_ctor_args_lvalue);
    add_test(test_block_stack_ctor_args_rvalue);
    add_test(test_block_stack_ctor_errors);
    add_test(test_block_stack_compare);
    add_test(test_block_stack_equal);
    add_test(test_block_stack_serialisation);

    return tests;
}

void init_test_block(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_block_");
    m.def("get_block_tests", &get_block_tests);
    m.def("get_block_stack_tests", &get_block_stack_tests);
}
