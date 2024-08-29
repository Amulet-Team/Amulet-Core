#pragma once

#include <memory>
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace Amulet {
namespace collections {

	// A class to allow python to hold a reference to a smart pointer
	class Holder {
	public:
		virtual ~Holder() {}
	};

	template <typename T>
	class HolderTemplate: public Holder {
	private:
		T value;
	public:
		HolderTemplate(T&& value): value(std::move(value)){}
	};

}
}
