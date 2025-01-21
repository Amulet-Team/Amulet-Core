#pragma once

#include <set>
#include <stdexcept>
#include <vector>

namespace Amulet {

class NoValidSector : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

class Sector {
public:
    size_t start;
    size_t stop;

    Sector(size_t start = 0, size_t stop = 0)
        : start(start)
        , stop(stop)
    {
    }

    size_t length() const;

    // Do the two sectors intersect each other.
    bool intersects(const Sector& other) const;

    // Is the other sector entirely within this sector.
    bool contains(const Sector& other) const;

    // Do the two sectors neighbour but not intersect.
    bool neighbours(const Sector& other) const;

    // Split this sector around another sector.
    std::vector<Sector> split(const Sector& other) const;
};

// Sort by start position
struct SectorStartSort {
    bool operator()(const Sector& a, const Sector& b) const
    {
        return a.start < b.start;
    }
};

// Sort by length then start.
struct SectorLenghtStartSort {
    bool operator()(const Sector& a, const Sector& b) const
    {
        if (a.length() == b.length()) {
            return a.start < b.start;
        } else {
            return a.length() < b.length();
        }
    }
};

// A class to manage a contiguous group of sectors.
// This class is not thread safe. The owner must handle synchronisation.
class SectorManager {
private:
    size_t _stop;
    bool _resizable;

    // A list of free sectors ordered by start location
    std::set<Sector, SectorStartSort> _free_start;

    // A list of free sectors ordered by (length, start).
    //  This makes it easier to find the first sector large enough
    std::set<Sector, SectorLenghtStartSort> _free_size;

    // A set of reserved sectors
    std::set<Sector, SectorStartSort> _reserved;

public:
    SectorManager(size_t start = 0, size_t stop = 0, bool resizable = true)
        : _stop(stop)
        , _resizable(resizable)
    {
        if (stop < start) {
            throw std::invalid_argument("stop must be at least start");
        }
        _free_start.emplace(start, stop);
        _free_size.emplace(start, stop);
    };

    const std::set<Sector, SectorStartSort>& sectors() const { return _free_start; }

    Sector reserve_space(size_t length);
    void reserve(const Sector& sector);
    void free(const Sector& sector);
};

} // namespace Amulet
