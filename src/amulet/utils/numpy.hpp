#pragma once

#include <cstdint>
#include <vector>
#include <utility>
#include <span>
#include <unordered_map>


namespace Amulet {
    // dtypeT can be any numerical type.
    // inverseT must be large enough to store the length of arr.
    template <typename dtypeT, typename inverseT>
    void unique_inverse(const std::span<dtypeT> arr, std::vector<dtypeT>& unique, std::span<inverseT>& inverse){
        if (arr.size() != inverse.size()){
            throw std::invalid_argument("arr and inverse must have the same size.");
        }
        if (unique.size()){
            throw std::invalid_argument("unique must be empty.");
        }
        // Map from found values to their index in unique
        std::unordered_map<dtypeT, inverseT> value_to_index;

        for (inverseT i = 0; i < arr.size(); i++){
            dtypeT value = arr[i];
            auto it = value_to_index.find(value);
            if (it == value_to_index.end()){
                inverse[i] = unique.size();
                value_to_index[value] = unique.size();
                unique.push_back(value);
            } else {
                inverse[i] = it->second;
            }
        }
    }
}
