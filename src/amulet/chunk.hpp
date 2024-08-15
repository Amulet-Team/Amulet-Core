#pragma once

#include <string>
#include <unordered_map>
#include <optional>
#include <functional>
#include <memory>
#include <stdexcept>


namespace Amulet {
	typedef std::unordered_map<std::string, std::optional<std::string>> SerialisedComponents;

	class Chunk {
	public:
		virtual ~Chunk() {}
		virtual std::string get_chunk_id() = 0;
	private:
		friend class ChunkHandle;
		virtual std::vector<std::string> get_component_ids() = 0;
		virtual SerialisedComponents serialise_chunk() = 0;
		virtual void reconstruct_chunk(SerialisedComponents) = 0;
	};

	namespace detail {
		extern std::unordered_map<std::string, std::function<std::shared_ptr<Chunk>()>> chunk_constructors;
	}

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

	template <class ... Components>
	class ChunkComponentHelper: public Chunk, public Components... {
	public:
		// Null constructor
		ChunkComponentHelper() : Components()... {}
	private:
		// Component list
		std::vector<std::string> get_component_ids() {
			std::vector<std::string> component_ids;
			(
				[&]{
					component_ids.push_back(Components::ComponentID);
				}(),
				...
			);
			return component_ids;
		}
		// Serialiser
		SerialisedComponents serialise_chunk() {
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
		void reconstruct_chunk(SerialisedComponents component_data) {
			(
				[&]{
					Components::deserialise(component_data.extract(Components::ComponentID).mapped());
				}(),
				...
			);
		}
	};
}
