### This implements classes and methods to interface with the world data on disk 

###world_loader
amulet.world_interface.world_loader.load_world(directory: str, _format: str = None, forced: bool = False) -> Format
- finds the correct format loader and initiates it with the directory path
    
###format_loader and formats
amulet.world_interface.format_loader.get_format(format_id: str) -> Format
- called by the above to get the Format class for the given format_id

amulet.world_interface.formats
- a store for the different formats

###interface_loader and interfaces
Interfaces are the classes that actually interface with the world data
amulet.world_interface.interface_loader.get_interface(interface_id: str) -> Interface
- get the interface for the given version
amulet.world_interface.interfaces
- a store for the different interfaces

###translator_loader and translators
Translators convert the data from one format into another format
