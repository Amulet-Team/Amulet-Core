import os
import sys
import traceback
import importlib
import importlib.util
import glob
import types
import time

_formats = {}

class _FormatLoader(object):

    REQUIRED_ATTRIBUTES = [
        'LEVEL_CLASS',
        'REGION_CLASS',
        'CHUNK_CLASS',
        'MATERIALS_CLASS',
        'identify'
    ]

    def __init__(self, search_directory=__file__):
        if os.path.isdir(search_directory):
            self.search_directory = search_directory
        else:
            self.search_directory = os.path.dirname(search_directory)

        self._find_formats()

    def _find_formats(self):
        global _formats
        directories = glob.glob(os.path.join(self.search_directory, '*', ''))
        sys.path.insert(0, os.path.join(self.search_directory))
        for d in directories:
            if not os.path.exists(os.path.join(d, '__init__.py')):
                continue
            format_name = os.path.basename(os.path.dirname(d)[2:])
            success, module = self.load_format(format_name)
            if success:
                _formats[format_name] = module

    def load_format(self, directory):
        try:
            format_module = importlib.import_module(os.path.basename(directory))
            #spec = importlib.util.find_spec(directory)
            #print('spec', spec)
            #format_module = importlib.util.module_from_spec(spec)
            #spec.loader.exec_module(format_module)
        except Exception as e:
            traceback.print_exc()
            time.sleep(0.01)
            print('Could not import the "{}" format due to the above Exception'.format(directory))
            return False, None
        for attr in self.REQUIRED_ATTRIBUTES:
            if not hasattr(format_module, attr):
                print('Disabled the "{}" format due to missing required attributes'.format(directory))
                return False, None
        return True, format_module

    def reload(self):
        self._find_formats()

    def add_external_format(self, name, module):
        global _formats
        if isinstance(name, str) and isinstance(module, types.ModuleType) and name not in _formats:
            _formats[name] = module
        elif name in _formats:
            raise Exception('You cannot override an already loaded world format')
        else:
            raise Exception('To add an external format you must supply a name and a module object!')

def load_world(world_directory):
    for format_module in _formats.itervalues():
        if format_module.identify(world_directory):
            return format_module.LEVEL_CLASS(world_directory)
    return None

loader = _FormatLoader()