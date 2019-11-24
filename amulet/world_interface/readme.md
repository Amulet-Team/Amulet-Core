### This implements classes and methods to interface with the world data on disk 

### Summary
Formats sit between the universal world class and the world on disk.
The World class requests chunks from the Format class.
The Format class loads the chunks from disk and uses an Interface class to unpack that data.
It then uses a Translator to translate that data to the universal format


### world_interface
amulet.world_interface.load_world(directory: str, _format: str = None, forced: bool = False) -> World
- finds the correct format and initiates a World class using it
    
### formats
amulet.world_interface.formats.get_format(format_id: str) -> Format
- called by the above to get the Format class for the given format_id
- deals with the whole world and processes requests to load and save chunks
- gets chunks from disk before passing them through an interface and translator to get a universal Chunk
- the reverse of this to go the other direction

### interfaces
Interfaces are the classes that actually interface with the chunk data.
They take the raw data in whatever form the Format class loads it in and organises it into a Chunk class
amulet.world_interface.interfaces.loader.get(identifier: Tuple) -> Interface:
- get the interface for the given version

### translators
Translators convert a Chunk class in version format to a Chunk class in Universal format (or back)
amulet.world_interface.translators.loader.get(identifier: Tuple) -> Translator:
- get the interface for the given version

## loading and saving workflow
### load:
load raw_data
interface.decode(raw_data) -> Chunk, palette (version)
    palette
    
        Java numerical: numpy.ndarray[n*2 int]
        Java blockstate: numpy.ndarray[Block]
        
        Bedrock numerical: numpy.ndarray[
            Tuple[
                Tuple[None, Tuple[int, int]]
            ]
        ]
        
        Bedrock psudo-numerical: numpy.ndarray[
            Tuple[
                Union[
                    Tuple[None, Tuple[int, int]],
                    Tuple[None, Block]
                ], ...
            ]
        ]
        
        Bedrock nbt-blockstate: numpy.ndarray[
            Tuple[
                Union[
                    Tuple[None, Tuple[int, int]],
                    Tuple[None, Block],
                    Tuple[Tuple[int, int, int, int], Block]
                ], ...
            ]
        ]
        
translator.to_universal(Chunk, palette) -> Chunk, palette (universal)
    palette: numpy.ndarray[Block]
		
### save:
translator.from_universal(Chunk, palette) -> Chunk, palette (version)
    palette
    
        Java numerical: numpy.ndarray[n*2 int]
        Java blockstate: numpy.ndarray[Block]
        
        Bedrock numerical: numpy.ndarray[
            Tuple[
                Tuple[None, Tuple[int, int]], ...
            ]
        ]
        
        Bedrock psudo-numerical: numpy.ndarray[
            Tuple[
                Tuple[None, Block], ...
            ]
        ]
        
        Bedrock nbt-blockstate: numpy.ndarray[
            Tuple[
                Tuple[Tuple[int, int, int, int], Block], ...
            ]
        ]
        
interface.encode(Chunk, palette) -> raw_data
save raw_data
