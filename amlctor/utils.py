from importlib.util import spec_from_file_location
from pathlib import Path





def get_settingspy_module(path: Path) -> dict:
        """ 
                returns names from the `settings.py` modul of the pipeline `path` directory 
                path:           pipeline path
                returns:        dict of names from the module. 
        """
        path_settingspy = str(path / 'settings.py')
        spec = spec_from_file_location('settings', path_settingspy)
        dirs = dir(spec.loader.load_module())
        dirs = [dir for dir in dirs if  not dir.startswith('__') and dir.endswith('__')]
        kws = {}
        module = spec.loader.load_module()
        for kw in dirs:
                kws[kw] = module.__dict__[kw]

        return kws

        
         



