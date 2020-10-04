"""
local history manager
    key based storage
        When a piece of data is loaded from disk it needs to be stored as revision 0
        If a piece of data is deleted it should be stored as None to specify that the data has been deleted
        If a piece of data was created rather than loaded from disk the revision 0 should be populated as None
            to specify that the revision 0 did not exist and the data should be added as revision 1
        It needs to store the revision index that is current within the editor.
        It also needs to store the revision that is saved to disk so that we know what has changed compared to
            the current save state rather than the original save state.
        If the above two indexes do not match then the data has been changed compared to the saved version so it needs saving.
    global storage
        We need to store a list of pools of keys that have changed for each undo point.
        We also need to store the index of which pool is current. This will get changed when undoing/redoing to keep track.


    When the creation of an undo point is requested
        we should scan all of the objects and see if the `changed` flag has been set to `True`.
        If this is the case the data has been changed and we should create a backup of it.
            make sure to reset the `changed` flag to False for the cached version
        A new revision for each entry is created and the current revision index is incremented.
        A pool of keys that have changed should be created.
            When undoing this change we look at this pool to see what changed and undo each of those.
            The same applies when redoing
        Finally the `changed` flags for each of the entries should be changed to False so that the next
            undo point only catches what has changed since this undo point.
            The better solution here is to empty the temporary database and re-populate from the latest cache
                revision where the `changed` flag was already set to False. This also solves the issue where
                the data was modified but the `changed` flag was not set to True by the script.

global history manager
    would store each of the local history managers
    would be the entry
"""

from .changeable import Changeable
