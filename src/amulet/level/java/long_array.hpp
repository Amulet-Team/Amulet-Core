#pragma once
#include <span>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <cmath>

namespace Amulet {
	/*
	Minecraft Java edition stores the block and height arrays in a compacted long array format.
	The format stores one or more entries per long, using the fewest number of bits required to store the data.
	There are two storage methods, the compact version was used prior to 1.16 and the less compact version in 1.16 and above.
	Apparently the less compact version is quicker to pack and unpack.
	The compact version effectively stores the values as a bit array spanning one or more values in the long array.
	There may be some padding if the bit array does not fill all the long values. (The letter "P" signifies an unused padding bit)
	HGGGGGGGGGFFFFFFFFFEEEEEEEEEDDDDDDDDDCCCCCCCCCBBBBBBBBBAAAAAAAAA PPNNNNNNNNNMMMMMMMMMLLLLLLLLLKKKKKKKKKJJJJJJJJJIIIIIIIIIHHHHHHHH
	The less compact version does not allow entries to straddle long values. Instead, if required, there is padding within each long.
	PGGGGGGGGGFFFFFFFFFEEEEEEEEEDDDDDDDDDCCCCCCCCCBBBBBBBBBAAAAAAAAA PNNNNNNNNNMMMMMMMMMLLLLLLLLLKKKKKKKKKJJJJJJJJJIIIIIIIIIHHHHHHHHH
	*/

	template <typename dstT>
	void decode_long_array(
		const std::span<std::uint64_t>& src,  // The long array to decode
		std::span<dstT>& dst,  // The array to unpack values into
		std::uint8_t bits_per_entry,  // The number of bits per entry
		bool dense = true
	) {
		if (bits_per_entry < 1 || 64 < bits_per_entry) {
			throw std::invalid_argument("bits_per_entry must be between 1 and 64 inclusive. Got " + std::to_string(bits_per_entry));
		}

		size_t expected_len = std::ceil(
			dense ? static_cast<float>(dst.size()) * bits_per_entry / 64 : static_cast<float>(dst.size()) / (64 / bits_per_entry)
		);

		if (src.size() != expected_len) {
			throw std::invalid_argument(
				dense ? "Dense encoded long array with " : "Encoded long array with " +
				std::to_string(bits_per_entry) +
				" bits per entry should contain " +
				std::to_string(expected_len) +
				" longs but got " +
				std::to_string(src.size()) +
				"."
			);
		}

		size_t entries_per_long = 64 / bits_per_entry;
		const std::uint64_t mask = std::pow(2, bits_per_entry) - 1;
		if (dense) {
			for (size_t dst_index = 0; dst_index < dst.size(); dst_index++) {
				size_t bit_start = dst_index * bits_per_entry;
				size_t bit_stop = (dst_index + 1) * bits_per_entry;
				size_t long_start = bit_start / 64;
				dstT& value = dst[dst_index];
				value = (src[long_start] >> (bit_start % 64)) & mask;
				if ((long_start + 1) * 64 < bit_stop) {
					// Overflows into the next long
					size_t overflow_bits = bit_stop - (long_start + 1) * 64;
					size_t previous_bits = bits_per_entry - overflow_bits;
					value |= (src[long_start + 1] & (mask >> previous_bits)) << previous_bits;
				}
			}
		}
		else {
			const std::uint64_t mask = std::pow(2, bits_per_entry) - 1;
			size_t dst_index = 0;
			for (const auto& src_value : src) {
				for (
					size_t offset = 0;
					offset < entries_per_long && dst_index < dst.size();
					offset++, dst_index++
				) {
					dst[dst_index] = (src_value >> (bits_per_entry * offset)) & mask;
				}
			}
		}
	}
}
