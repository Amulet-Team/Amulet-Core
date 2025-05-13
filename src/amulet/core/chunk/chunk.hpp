#pragma once

#include <functional>
#include <memory>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>

#include <amulet/core/dll.hpp>

// Requirements:
// Split chunk data into components that are orthogonal to each other.
// create a chunk with all components default initialised.
// reconstruct a chunk from a subset of its components.
// reconstruct a chunk with all components.
// query if a chunk has a component. (isinstance/is_base_of/dynamic_cast or has_component)
// get a component. (method/property or get_component)
// set and validate a component. (method/property or set_component)
// serialise loaded components.

namespace Amulet {
typedef std::unordered_map<std::string, std::optional<std::string>> SerialisedChunkComponents;

// The abstract chunk class
class Chunk {
public:
    virtual ~Chunk() = default;
    virtual std::string get_chunk_id() const = 0;
    virtual std::set<std::string> get_component_ids() const = 0;
    // private:
    //  These are public but may become private one day
    virtual SerialisedChunkComponents serialise_chunk() const = 0;
    virtual void reconstruct_chunk(SerialisedChunkComponents) = 0;
};

namespace detail {
    using ChunkContructor = std::function<std::shared_ptr<Chunk>()>;
    AMULET_CORE_EXPORT void add_null_chunk_constructor(const std::string& id, ChunkContructor constructor);
    AMULET_CORE_EXPORT void remove_null_chunk_constructor(const std::string& id);
}

AMULET_CORE_EXPORT std::shared_ptr<Chunk> get_null_chunk(std::string chunk_id);

// An object that concrete chunk classes must be registered with.
// This enables reconstructing the chunk class.
template <typename ChunkT>
class ChunkNullConstructor {
public:
    ChunkNullConstructor()
    {
        detail::add_null_chunk_constructor(ChunkT::ChunkID, []() {
            return std::make_shared<ChunkT>();
        });
    }
    ~ChunkNullConstructor()
    {
        detail::remove_null_chunk_constructor(ChunkT::ChunkID);
    }
};

// A utility class to simplify component serialisation and deserialisation.
template <class ChunkBaseClass, class... Components>
class ChunkComponentHelper : public ChunkBaseClass, public Components... {
public:
    // Component list
    std::set<std::string> get_component_ids() const override
    {
        std::set<std::string> component_ids;
        (
            [&] {
                component_ids.emplace(Components::ComponentID);
            }(),
            ...);
        return component_ids;
    }
    // These are public but may become private one day
    // Null constructor
    ChunkComponentHelper()
        : Components()...
    {
    }
    // private:
    // Serialiser
    SerialisedChunkComponents serialise_chunk() const override
    {
        SerialisedChunkComponents component_data;
        (
            [&] {
                component_data[Components::ComponentID] = Components::serialise();
            }(),
            ...);
        return component_data;
    }
    // Deserialiser
    void reconstruct_chunk(SerialisedChunkComponents component_data) override
    {
        (
            [&] {
                auto node = component_data.extract(Components::ComponentID);
                Components::deserialise(node ? node.mapped() : std::nullopt);
            }(),
            ...);
    }
};

class AMULET_CORE_EXPORT_EXCEPTION ChunkLoadError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
    ChunkLoadError()
        : ChunkLoadError("ChunkLoadError")
    {
    }
};

class AMULET_CORE_EXPORT_EXCEPTION ChunkDoesNotExist : public ChunkLoadError {
public:
    using ChunkLoadError::ChunkLoadError;
    ChunkDoesNotExist()
        : ChunkDoesNotExist("ChunkDoesNotExist")
    {
    }
};

} // namespace Amulet
