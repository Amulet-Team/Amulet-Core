#pragma once

#include <pybind11/pybind11.h>

#include <memory>

namespace py = pybind11;

namespace Amulet {
namespace collections {

	// A class to allow python to hold a reference to a smart pointer
	class Holder {
	public:
		virtual ~Holder() = default;
	};

	template <typename T>
	class HolderTemplate: public Holder {
	private:
		T value;
	public:
		HolderTemplate(T&& value): value(std::move(value)){}
	};

	template <typename T>
	static py::object make_holder(T&& value) {
		return py::cast(
			static_cast<std::unique_ptr<Holder>>(
				std::make_unique<HolderTemplate<T>>(
					std::move(value)
				)
			)
		);
	}

}
}
