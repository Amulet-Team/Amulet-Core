### This implements classes and methods to interface with the world data on disk 

###Summary
Formats sit between the universal world class and the world on disk.
The World class requests chunks from the Format class.
The Format class loads the chunks from disk and uses an Interface class to unpack that data.
It then uses a Translator to translate that data to the universal format


###world_loader
amulet.world_interface.world_loader.load_world(directory: str, _format: str = None, forced: bool = False) -> World
- finds the correct format loader and initiates a World class using it
    
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
