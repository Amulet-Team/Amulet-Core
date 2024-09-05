#pragma once

#include <tuple>
#include <unordered_map>
#include <variant>
#include <cstdint>
#include <vector>
#include <span>
#include <cstdlib>
#include <type_traits>
#include <memory>
#include <stdexcept>

#include <amulet/io/binary_writer.hpp>
#include <amulet/io/binary_reader.hpp>


namespace Amulet {
	namespace detail {
		template <typename T>
		inline std::unique_ptr<T*> new_buffer(size_t count) {
			T* buffer = (T*) std::malloc(sizeof(T) * count);
			if (buffer == nullptr) {
				throw std::runtime_error("Could not allocate buffer");
			}
			return std::make_unique<T*>(buffer);
		}
	}

	typedef std::tuple<std::uint16_t, std::uint16_t, std::uint16_t> SectionShape;

	class IndexArray3D {
	private:
		SectionShape _shape;
		size_t _size;
		std::unique_ptr<std::uint32_t*> _buffer;
	public:
		IndexArray3D(const SectionShape& shape) :
			_shape(shape),
			_size(std::get<0>(shape)* std::get<1>(shape)* std::get<2>(shape)),
			_buffer(detail::new_buffer<std::uint32_t>(_size))
		{}
		IndexArray3D(const SectionShape& shape, std::uint32_t value) :
			IndexArray3D(shape) {
			std::fill_n(*_buffer, _size, value);
		}
		IndexArray3D(const IndexArray3D& other):
			IndexArray3D(other.get_shape())
		{
			std::memcpy(*_buffer, *other._buffer, sizeof(std::uint32_t) * other.get_size());
		}

		void serialise(BinaryWriter&) const;
		static std::shared_ptr<IndexArray3D> deserialise(BinaryReader&);

		const SectionShape& get_shape() const {
			return _shape;
		}
		const size_t& get_size() const { return _size; }
		std::uint32_t* get_buffer() const { return *_buffer; }
	};

	namespace detail {
		inline void validate_array_shape(
			const std::shared_ptr<IndexArray3D>& default_array,
			const SectionShape& array_shape
		) {
			if (default_array->get_shape() != array_shape) {
				throw std::invalid_argument("Array shape does not match required shape.");
			}
		}

		inline void validate_array_shape(
			const std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>>& default_array,
			const SectionShape& array_shape
		) {
			if (std::holds_alternative<std::shared_ptr<IndexArray3D>>(default_array)) {
				validate_array_shape(std::get<std::shared_ptr<IndexArray3D>>(default_array), array_shape);
			}
		}
	}

	class SectionArrayMap {
	private:
		SectionShape _array_shape;
		std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> _default_array;
		std::unordered_map<std::int64_t, std::shared_ptr<IndexArray3D>> _arrays;
	public:
		SectionArrayMap(
			const SectionShape& array_shape,
			std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array
		) : _array_shape(array_shape), _default_array(default_array), _arrays() {
			detail::validate_array_shape(_default_array, _array_shape);
		}

		void serialise(BinaryWriter&) const;
		static std::shared_ptr<SectionArrayMap> deserialise(BinaryReader&);

		const SectionShape& get_array_shape() const { return _array_shape; }
		
		std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> get_default_array() const { return _default_array; }
		
		void set_default_array(std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array) {
			detail::validate_array_shape(default_array, _array_shape);
			_default_array = default_array;
		}

		const std::unordered_map<std::int64_t, std::shared_ptr<IndexArray3D>>& get_arrays() const {
			return _arrays;
		}

		size_t get_size() const { return _arrays.size(); }

		bool contains_section(std::int64_t cy) const {
			return _arrays.contains(cy);
		}

		std::shared_ptr<IndexArray3D> get_section(std::int64_t cy) const {
			return _arrays.at(cy);
		}

		void set_section(std::int64_t cy, std::shared_ptr<IndexArray3D> section) {
			detail::validate_array_shape(section, _array_shape);
			_arrays[cy] = section;
		}

		void populate_section(std::int64_t cy) {
			if (_arrays.contains(cy)) {
				return;
			}
			std::visit([this, &cy](auto&& arg) {
				using T = std::decay_t<decltype(arg)>;
				if constexpr (std::is_same_v<T, std::uint32_t>) {
					_arrays[cy] = std::make_shared<IndexArray3D>(_array_shape, arg);
				}
				else {
					_arrays[cy] = std::make_shared<IndexArray3D>(*arg);
				}
				}, _default_array);
		}

		void del_section(std::int64_t cy) {
			_arrays.erase(cy);
		}
	};

}
