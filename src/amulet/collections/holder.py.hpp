#pragma once

namespace Amulet {
namespace collections {

	// A class to allow python to hold a reference to a smart pointer
	class Holder {
	public:
		virtual ~Holder() {};
	};

	template <typename T>
	class HolderTemplate {
	private:
		T value;
	public:
		HolderTemplate(T value): value(value){}
	};

}
}
