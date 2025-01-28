#include "sector_manager.hpp"
#include <set>
#include <vector>

namespace Amulet {

size_t Sector::length() const { return stop - start; }

// Do the two sectors intersect each other.
bool Sector::intersects(const Sector& other) const
{
    return !(other.stop <= start || stop <= other.start);
}

// Is the other sector entirely within this sector.
bool Sector::contains(const Sector& other) const
{
    return start <= other.start && other.stop <= stop;
}

// Do the two sectors neighbour but not intersect.
bool Sector::neighbours(const Sector& other) const
{
    return other.stop == start or stop == other.start;
}

// Split this sector around another sector.
std::vector<Sector> Sector::split(const Sector& other) const
{
    std::vector<Sector> sectors;
    if (start < other.start) {
        if (other.start < stop) {
            sectors.emplace_back(start, other.start);
        } else {
            sectors.emplace_back(start, stop);
        }
    }
    if (other.stop < stop) {
        if (other.stop < start) {
            sectors.emplace_back(start, stop);
        } else {
            sectors.emplace_back(other.stop, stop);
        }
    }
    return sectors;
}

Sector SectorManager::reserve_space(size_t length)
{
    if (length == 0) {
        throw std::invalid_argument("Cannot reserve a sector with zero length.");
    }
    auto it = _free_size.upper_bound(Sector(0, length));
    if (it != _free_size.end()) {
        // There exists a section large enough to fit the length
        Sector free_sector = *it;
        // Remove the section from the free sections
        it = _free_size.erase(it);
        _free_start.erase(free_sector);
        // Create the reserved sector.
        Sector sector(free_sector.start, free_sector.start + length);
        if (length < free_sector.length()) {
            // Re-add the remainder to the free sections.
            _free_size.emplace_hint(it, sector.stop, free_sector.stop);
            _free_start.emplace(sector.stop, free_sector.stop);
        }
        _reserved.emplace(sector);
        return sector;
    } else if (_resizable) {
        // Resize to fit
        Sector sector(_stop, _stop + length);
        _stop = sector.stop;
        _reserved.emplace(sector);
        return sector;
    } else {
        throw NoValidSector("There is not enough contiguous space to allocate the length.");
    }
};

void SectorManager::reserve(const Sector& sector)
{
    if (sector.length() == 0) {
        throw std::invalid_argument("Cannot reserve a sector with zero length.");
    }
    if (_stop <= sector.start && (_free_size.empty() || _free_size.rbegin()->stop != _stop)) {
        // Sector starts beyond the end and the last sector is reserved.
        if (_resizable) {
            _free_start.emplace(_stop, sector.stop);
            _free_size.emplace(_stop, sector.stop);
            _stop = sector.stop;
        } else {
            throw NoValidSector("The sector starts outside of the region.");
        }
    }

    // Find the first sector that starts before or at the sector start.
    auto it = _free_start.lower_bound(sector);
    if (it != _free_start.end() && it->start == sector.start) {
        // Found the correct sector
    } else if (it != _free_start.begin()) {
        // Seek to the previous value if this is not the beginning.
        it--;
    } else {
        throw NoValidSector("No free sectors that start at or before the one being reserved.");
    }

    Sector free_sector = *it;
    if (sector.stop <= free_sector.stop) {
        // The sector fits within the contained sector
        // remove the contained sector
        it = _free_start.erase(it);
        _free_size.erase(free_sector);
    } else if (free_sector.stop == _stop) {
        if (_resizable) {
            // The sector is the last one and the memory region is resizable
            it = _free_start.erase(it);
            _free_size.erase(free_sector);
            free_sector = Sector(free_sector.start, sector.stop);
            _stop = sector.stop;
        } else {
            throw NoValidSector("The sector is outside the defined region and the region is not resizable.");
        }
    } else {
        throw NoValidSector("The requested sector is not free to be reserved.");
    }

    for (const auto& sec : free_sector.split(sector)) {
        _free_start.emplace_hint(it, sec);
        _free_size.emplace(sec);
    }
    _reserved.emplace(sector);
};

void SectorManager::free(const Sector& sector)
{
    auto reserved_it = _reserved.find(sector);
    if (reserved_it == _reserved.end() || reserved_it->stop != sector.stop) {
        throw std::invalid_argument("Sector was not reserved");
    }
    // remove the sector from the reserved storage
    _reserved.erase(reserved_it);

    // Find the first sector that starts before or at the sector start.
    auto free_it = _free_start.upper_bound(sector);

    Sector new_sector = sector;
    if (free_it != _free_start.end() && free_it->start == new_sector.stop) {
        // The next free sector starts at the end of the freed sector. Merge them.
        new_sector.stop = free_it->stop;
        _free_size.erase(*free_it);
        free_it = _free_start.erase(free_it);
    }

    if (free_it != _free_start.begin() && (--free_it)->stop == new_sector.start) {
        // The previous free sector starts at the beginning of the freed sector. Merge them.
        new_sector.start = free_it->start;
        _free_size.erase(*free_it);
        free_it = _free_start.erase(free_it);
    }

    _free_start.emplace_hint(free_it, new_sector);
    _free_size.emplace(new_sector);
};

} // namespace Amulet
