#include <memory>

#include <pybind11/pybind11.h>

#include <amulet/block.hpp>
#include <amulet/biome.hpp>
#include <amulet/chunk.hpp>
#include <amulet/chunk_components/block_component.hpp>

#include "java_chunk.hpp"
#include "chunk_components/java_raw_chunk_component.hpp"
#include "chunk_components/data_version_component.hpp"

namespace py = pybind11;


void init_java_chunk(py::module m) {
    py::class_<
        Amulet::JavaChunk,
        std::shared_ptr<Amulet::JavaChunk>,
        Amulet::Chunk
    >
        JavaChunk(m, "JavaChunk");

    py::class_<
        Amulet::JavaChunkNA, 
        std::shared_ptr<Amulet::JavaChunkNA>,
        Amulet::JavaChunk,
        Amulet::JavaRawChunkComponent,
        Amulet::DataVersionComponent,
        // Amulet::LastUpdateComponent,
        // Amulet::JavaLegacyVersionComponent,
        Amulet::BlockComponent//,
        // Amulet::BlockEntityComponent,
        // Amulet::EntityComponent,
        // Amulet::Biome2DComponent,
        // Amulet::Height2DComponent,
    >
        JavaChunkNA(m, "JavaChunkNA");

    JavaChunkNA.def(
        py::init<
            std::shared_ptr<Amulet::BlockStack>,
            std::shared_ptr<Amulet::Biome>
        >(),
        py::arg("default_block"),
        py::arg("default_biome")
    );

    py::class_<
        Amulet::JavaChunk0,
        std::shared_ptr<Amulet::JavaChunk0>,
        Amulet::JavaChunk,
        Amulet::JavaRawChunkComponent,
        Amulet::DataVersionComponent,
        // Amulet::LastUpdateComponent,
        // Amulet::TerrainPopulatedComponent,
        // Amulet::LightPopulatedComponent,
        Amulet::BlockComponent//,
        // Amulet::BlockEntityComponent,
        // Amulet::EntityComponent,
        // Amulet::Biome2DComponent,
        // Amulet::Height2DComponent,
    >
        JavaChunk0(m, "JavaChunk0");

    JavaChunk0.def(
        py::init<
            std::int64_t,
            std::shared_ptr<Amulet::BlockStack>,
            std::shared_ptr<Amulet::Biome>
        >(),
        py::arg("data_version"),
        py::arg("default_block"),
        py::arg("default_biome")
    );

    py::class_<
        Amulet::JavaChunk1444,
        std::shared_ptr<Amulet::JavaChunk1444>,
        Amulet::JavaChunk,
        Amulet::JavaRawChunkComponent,
        Amulet::DataVersionComponent,
        // Amulet::LastUpdateComponent,
        // Amulet::StatusStringComponent,
        Amulet::BlockComponent//,
        // Amulet::BlockEntityComponent,
        // Amulet::EntityComponent,
        // Amulet::Biome2DComponent,
        // Amulet::Height2DComponent,
    >
        JavaChunk1444(m, "JavaChunk1444");

    JavaChunk1444.def(
        py::init<
        std::int64_t,
        std::shared_ptr<Amulet::BlockStack>,
        std::shared_ptr<Amulet::Biome>
        >(),
        py::arg("data_version"),
        py::arg("default_block"),
        py::arg("default_biome")
    );

    py::class_<
        Amulet::JavaChunk1466,
        std::shared_ptr<Amulet::JavaChunk1466>,
        Amulet::JavaChunk,
        Amulet::JavaRawChunkComponent,
        Amulet::DataVersionComponent,
        // Amulet::LastUpdateComponent,
        // Amulet::StatusStringComponent,
        Amulet::BlockComponent//,
        // Amulet::BlockEntityComponent,
        // Amulet::EntityComponent,
        // Amulet::Biome2DComponent,
        // Amulet::NamedHeight2DComponent,
    >
        JavaChunk1466(m, "JavaChunk1466");

    JavaChunk1466.def(
        py::init<
        std::int64_t,
        std::shared_ptr<Amulet::BlockStack>,
        std::shared_ptr<Amulet::Biome>
        >(),
        py::arg("data_version"),
        py::arg("default_block"),
        py::arg("default_biome")
    );

    py::class_<
        Amulet::JavaChunk2203,
        std::shared_ptr<Amulet::JavaChunk2203>,
        Amulet::JavaChunk,
        Amulet::JavaRawChunkComponent,
        Amulet::DataVersionComponent,
        // Amulet::LastUpdateComponent,
        // Amulet::StatusStringComponent,
        Amulet::BlockComponent//,
        // Amulet::BlockEntityComponent,
        // Amulet::EntityComponent,
        // Amulet::Biome3DComponent,
        // Amulet::NamedHeight2DComponent,
    >
        JavaChunk2203(m, "JavaChunk2203");

    JavaChunk2203.def(
        py::init<
        std::int64_t,
        std::shared_ptr<Amulet::BlockStack>,
        std::shared_ptr<Amulet::Biome>
        >(),
        py::arg("data_version"),
        py::arg("default_block"),
        py::arg("default_biome")
    );

}
