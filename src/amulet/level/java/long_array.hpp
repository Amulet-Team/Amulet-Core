#pragma once
#include <algorithm>
#include <bit>
#include <cmath>
#include <cstdint>
#include <span>
#include <stdexcept>
#include <string>
#include <type_traits>

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

// Get the number of longs required to store the encoded long array.
inline size_t encoded_long_array_size(
    size_t decoded_size, // The number of elements to encode
    std::uint8_t bits_per_entry, // The number of bits of each number to use
    bool dense = true)
{
    if (dense) {
        // Total number of decoded bits ceiling divided by number of bits in a long.
        return (decoded_size * bits_per_entry + 63) / 64;
    } else {
        // The number of entries that can fit in one long.
        size_t entries_per_long = 64 / bits_per_entry;
        // The number of longs required to fit all entries.
        return (decoded_size + entries_per_long - 1) / entries_per_long;
    }
}

template <typename decodedT>
void decode_long_array(
    const std::span<std::uint64_t>& encoded, // The long array to decode
    std::span<decodedT>& decoded, // The array to unpack values into
    std::uint8_t bits_per_entry, // The number of bits per entry
    bool dense = true)
{
    static_assert(std::is_unsigned_v<decodedT>, "decodedT must be unsigned");
    if (bits_per_entry < 1 || 64 < bits_per_entry) {
        throw std::invalid_argument("bits_per_entry must be between 1 and 64 inclusive. Got " + std::to_string(bits_per_entry));
    }

    size_t encoded_len = encoded_long_array_size(decoded.size(), bits_per_entry, dense);
    if (encoded.size() != encoded_len) {
        throw std::invalid_argument(
            dense ? "Dense encoded long array with " : "Encoded long array with " + std::to_string(bits_per_entry) + " bits per entry should contain " + std::to_string(encoded_len) + " longs but got " + std::to_string(encoded.size()) + ".");
    }

    const std::uint64_t mask = ~0ull >> (64 - bits_per_entry);
    if (dense) {
        for (size_t decoded_index = 0; decoded_index < decoded.size(); decoded_index++) {
            size_t bit_start = decoded_index * bits_per_entry;
            size_t bit_stop = (decoded_index + 1) * bits_per_entry;
            size_t long_start = bit_start / 64;
            decodedT& value = decoded[decoded_index];
            value = static_cast<decodedT>((encoded[long_start] >> (bit_start % 64)) & mask);
            if ((long_start + 1) * 64 < bit_stop) {
                // Overflows into the next long
                size_t overflow_bits = bit_stop - (long_start + 1) * 64;
                size_t previous_bits = bits_per_entry - overflow_bits;
                value |= (encoded[long_start + 1] & (mask >> previous_bits)) << previous_bits;
            }
        }
    } else {
        size_t entries_per_long = 64 / bits_per_entry;
        size_t decoded_index = 0;
        for (const auto& encoded_value : encoded) {
            for (
                size_t offset = 0;
                offset < entries_per_long && decoded_index < decoded.size();
                offset++, decoded_index++) {
                decoded[decoded_index] = static_cast<decodedT>((encoded_value >> (bits_per_entry * offset)) & mask);
            }
        }
    }
}

// Encode the array to a long array with the specified number of bits. Extra bits are ignored.
template <typename decodedT>
void encode_long_array(
    const std::span<decodedT>& decoded, // The array to encode
    std::span<std::uint64_t> encoded, // The array to encode into. This must be large enough.
    std::uint8_t bits_per_entry, // The number of bits of each number to use
    bool dense = true)
{
    static_assert(std::is_unsigned_v<decodedT>, "decodedT must be unsigned");
    if (bits_per_entry < 1 || 64 < bits_per_entry) {
        throw std::invalid_argument("bits_per_entry must be between 1 and 64 inclusive. Got " + std::to_string(bits_per_entry));
    }

    // Set all values to 0
    std::fill(encoded.begin(), encoded.end(), 0);
    const std::uint64_t mask = ~0ull >> (64 - bits_per_entry);
    if (dense) {
        for (size_t decoded_index = 0; decoded_index < decoded.size(); decoded_index++) {
            // The bit in the array where the value starts
            size_t bit_start = decoded_index * bits_per_entry;
            // The bit in the array where the value stops
            size_t bit_stop = bit_start + bits_per_entry;
            // The long number that the value starts in
            size_t long_start = bit_start / 64;
            // The bit offset in the long where the value starts
            size_t long_bit_offset = bit_start % 64;
            // The bit in the array where the long stops
            size_t long_bit_stop = (long_start + 1) * 64;
            decodedT& value = decoded[decoded_index];
            encoded[long_start] = (encoded[long_start] & ~(mask << long_bit_offset)) + ((value & mask) << long_bit_offset);
            if (long_bit_stop < bit_stop) {
                // Overflows into the next long
                // The number of bits that overflow into the next long
                size_t overflow_bits = bit_stop - long_bit_stop;
                // The number of bits in the previous long
                size_t previous_bits = bits_per_entry - overflow_bits;
                encoded[long_start + 1] = (encoded[long_start + 1] & ~(mask >> previous_bits)) + ((value & mask) >> previous_bits);
            }
        }
    } else {
        size_t entries_per_long = 64 / bits_per_entry;
        size_t decoded_index = 0;
        size_t long_count = (decoded.size() + entries_per_long - 1) / entries_per_long;
        for (size_t encoded_index = 0; encoded_index < long_count; encoded_index++) {
            auto& encoded_value = encoded[encoded_index];
            encoded_value = 0;
            for (
                size_t offset = 0;
                offset < entries_per_long && decoded_index < decoded.size();
                offset++, decoded_index++) {
                std::uint64_t value = decoded[decoded_index] & mask;
                encoded_value += value << (bits_per_entry * offset);
            }
        }
    }
}

// Encode the array to a long aray with at least this number of bits. The number of required bits is computed before encoding.
template <typename decodedT>
void encode_long_array_min(
    const std::span<decodedT>& decoded, // The array to encode
    std::span<std::uint64_t> encoded, // The array to encode into
    std::uint8_t min_bits_per_entry, // The minimum number of bits of each number to use
    bool dense = true)
{
    static_assert(std::is_unsigned_v<decodedT>, "decodedT must be unsigned");
    if (min_bits_per_entry < 1 || 64 < min_bits_per_entry) {
        throw std::invalid_argument("min_bits_per_entry must be between 1 and 64 inclusive. Got " + std::to_string(min_bits_per_entry));
    }
    std::uint8_t bits_per_entry = std::max(
        min_bits_per_entry,
        std::bit_width(*std::max_element(decoded.begin(), decoded.end())));
    encode_long_array(decoded, encoded, bits_per_entry, dense);
}
}
