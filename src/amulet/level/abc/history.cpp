#include "history.hpp"

namespace Amulet {

// HistoryManagerPrivate

HistoryManagerPrivate::HistoryManagerPrivate()
{
    // Add an initial bin.
    history_bins.emplace_back();
}

void HistoryManagerPrivate::invalidate_future()
{
    // If there are future bins to invalidate.
    if (has_redo()) {
        // Destroy future bins
        history_bins.resize(history_index + 1);
        // Call invalidate_future for each layer
        for_each<AbstractHistoryManagerLayer>(
            layers,
            [](AbstractHistoryManagerLayer& layer) { layer.invalidate_future(); });
    }
}

bool HistoryManagerPrivate::has_redo()
{
    return history_index + 1 < history_bins.size();
}

// HistoryManager

HistoryManager::HistoryManager()
    : _h(std::make_shared<HistoryManagerPrivate>())
{
}

std::shared_mutex& HistoryManager::mutex()
{
    return _h->mutex;
}

void HistoryManager::reset()
{
    // Reset each layer
    for_each<AbstractHistoryManagerLayer>(
        _h->layers,
        [](AbstractHistoryManagerLayer& layer) { layer.reset(); });
    // Clear all history bins
    _h->history_bins.clear();
    // Add the initial bin.
    _h->history_bins.emplace_back();
    // Update the index to the initial bin.
    _h->history_index = 0;
}

void HistoryManager::mark_saved()
{
    for_each<AbstractHistoryManagerLayer>(
        _h->layers,
        [](AbstractHistoryManagerLayer& layer) { layer.mark_saved(); });
}

void HistoryManager::create_undo_bin()
{
    // Invalidate all future undo bins
    _h->invalidate_future();
    // Add a new bin
    _h->history_bins.emplace_back();
    _h->history_index++;
}

size_t HistoryManager::get_undo_count()
{
    return _h->history_index;
}

void HistoryManager::undo()
{
    // Check if there is anything to undo.
    if (_h->history_index == 0) {
        throw std::runtime_error("There is nothing to undo.");
    }
    // For all resources in the bin.
    for_each<HistoryResource>(
        _h->history_bins.at(_h->history_index),
        [](HistoryResource& resource) {
            // Decrement the index
            resource.index++;
            // Notify listeners that it has changed.
            resource.changed.emit();
        });
    // Decrement the history index.
    _h->history_index--;
}

size_t HistoryManager::get_redo_count()
{
    return _h->history_bins.size() - _h->history_index - 1;
}

void HistoryManager::redo()
{
    // Check if there is anything to redo.
    if (!_h->has_redo()) {
        throw std::runtime_error("There is nothing to redo.");
    }
    // Increment the history index.
    _h->history_index++;
    // For all resources in the bin.
    for_each<HistoryResource>(
        _h->history_bins.at(_h->history_index),
        [](HistoryResource& resource) {
            // Increment the index
            resource.index++;
            // Notify listeners that it has changed.
            resource.changed.emit();
        });
}

} // namespace Amulet
