#pragma once

#include <string>
#include <unordered_map>
#include <optional>
#include <functional>
#include <memory>
#include <stdexcept>

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
	typedef std::unordered_map<std::string, std::optional<std::string>> SerialisedComponents;

    // The abstract chunk class
	class Chunk {
	public:
		virtual ~Chunk() {}
		virtual std::string get_chunk_id() const = 0;
		virtual std::vector<std::string> get_component_ids() const = 0;
	//private:
	// These are public but may become private one day
		virtual SerialisedComponents serialise_chunk() const = 0;
		virtual void reconstruct_chunk(SerialisedComponents) = 0;
	};

	namespace detail {
		extern std::unordered_map<std::string, std::function<std::shared_ptr<Chunk>()>> chunk_constructors;
	}

	std::shared_ptr<Chunk> get_null_chunk(std::string chunk_id);

    // An object that concrete chunk classes must be registered with.
    // This enables reconstructing the chunk class.
	template <typename ChunkT>
	class ChunkNullConstructor {
	public:
		ChunkNullConstructor() {
			if (detail::chunk_constructors.contains(ChunkT::ChunkID)) {
				throw std::runtime_error("A chunk class has already been registered with ID " + ChunkT::ChunkID);
			}
			detail::chunk_constructors[ChunkT::ChunkID] = []() {
				return std::make_shared<ChunkT>();
			};
		};
		~ChunkNullConstructor() {
			detail::chunk_constructors.erase(ChunkT::ChunkID);
		};
	};

    // A utility class to simplify component serialisation and deserialisation.
	template <class ChunkBaseClass, class ... Components>
	class ChunkComponentHelper: public ChunkBaseClass, public Components... {
	public:
		// Component list
		std::vector<std::string> get_component_ids() const override {
			std::vector<std::string> component_ids;
			(
				[&]{
					component_ids.push_back(Components::ComponentID);
				}(),
				...
			);
			return component_ids;
		}
	// These are public but may become private one day
		// Null constructor
		ChunkComponentHelper() : Components()... {}
	//private:
		// Serialiser
		SerialisedComponents serialise_chunk() const override {
			SerialisedComponents component_data;
			(
				[&]{
					component_data[Components::ComponentID] = Components::serialise();
				}(),
				...
			);
			return component_data;
		}
		// Deserialiser
		void reconstruct_chunk(SerialisedComponents component_data) override {
			(
				[&]{
					Components::deserialise(component_data.extract(Components::ComponentID).mapped());
				}(),
				...
			);
		}
	};
}
