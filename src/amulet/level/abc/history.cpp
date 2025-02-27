#include "history.hpp"

namespace Amulet {

// HistoryManagerPrivate

HistoryManagerPrivate::HistoryManagerPrivate()
{
    history_bins.emplace_back();
}

void HistoryManagerPrivate::invalidate_future()
{
    if (has_redo()) {
        history_bins.resize(history_index + 1);
        for (auto& ptr : layers) {
            auto layer = ptr.lock();
            if (layer) {
                layer->invalidate_future();
            }
        }
    }
}

bool HistoryManagerPrivate::has_redo()
{
    return history_index + 1 < history_bins.size();
}

// HistoryManager

std::shared_mutex& HistoryManager::mutex()
{
    return _h->mutex;
}

void HistoryManager::reset()
{
    for (auto& ptr : _h->layers) {
        auto layer = ptr.lock();
        if (layer) {
            layer->reset();
        }
    }
    _h->history_bins.clear();
    _h->history_bins.emplace_back();
    _h->history_index = 0;
}

void HistoryManager::mark_saved()
{
    for (auto& ptr : _h->layers) {
        auto layer = ptr.lock();
        if (layer) {
            layer->mark_saved();
        }
    }
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
    throw std::runtime_error("NotImplementedError");
}

size_t HistoryManager::get_redo_count()
{
    return _h->history_bins.size() - _h->history_index - 1;
}

void HistoryManager::redo()
{
    throw std::runtime_error("NotImplementedError");
}

} // namespace Amulet
