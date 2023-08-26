from importlib.util import spec_from_file_location
from pathlib import Path
import re


	
def get_settingspy(path: Path) -> dict:
	""" 
		returns names from the `settings.py` modul of the pipeline `path` directory 
		path:           pipeline path
		returns:        dict of names from the module. 
	"""
	module_names = ('AML_MODULE_NAME', 'SCRIPT_MODULE_NAME', 'DATALOADER_MODULE_NAME')
	path_settingspy = str(path / 'settings/settings.py')
	spec = spec_from_file_location('settings', path_settingspy)
	dirs = dir(spec.loader.load_module())
	dirs = [dir for dir in dirs if  not dir.startswith('__') and not dir.endswith('__')]
	kws = {}
	module = spec.loader.load_module()
	for kw in dirs:
		kws[kw] = module.__dict__[kw]
	# module names for standartize .ext part - should be without extention
	for k in kws.keys():
		if k in module_names:
			if kws[k].endswith('.py'):
				kws[k] = kws[k].replace('.py', '')

	return kws



def is_pipe(path: Path, pipe_name: str = None, is_step: bool = False) -> bool:
	""" 
		Returns True if directory is pipeline. 
		Actually, checks if directory contains `files_to_check`.
		`pipe_name`:	if passed checks if name is exactly passed one
		`is_step`:		if True, pipe_name should be step_name
	"""
	contains_pipe = None
	# check if there is any pipe
	if path / 'settings' in path.iterdir():   # has settings dir
		settings_path = path / 'settings'
		files_to_check = ('.env', 'conda_dependencies.yml', 'settings.py')
		dir_files = [p.name for p in settings_path.iterdir()]
		for file in files_to_check:
			if not file in dir_files:
				return False						# path doesn't contain a pipe
			
		contains_pipe = True						# does.
	
	else:
		return False	# there is no any pipeline
	
	if pipe_name is None:
		return contains_pipe  # has an pipe and it's enough
	
	else:
		settingspy = get_settingspy(path)					# we have the name for checking
		if not isinstance(pipe_name, str):
			raise ValueError(f"Incorrect pipeline name '{pipe_name}' type: '{type(pipe_name)}'")
		
		if is_step is False:	# name is pipeline name
			return settingspy['NAME'] == pipe_name

		elif is_step is True:
			for step in settingspy['STEPS']:
				if pipe_name == step.name:
					return True		# step name found
			return False			# not fount
		else:
			raise ValueError(f"'is_step' should be boolean not '{type(is_step)}'")
			

def is_pipe_raise(path: Path, pipe_name: str = None, is_step: bool = False) -> bool:
	""" The same as `is_pipe` but raises exceptions in False casees """
	r = is_pipe(path, pipe_name, is_step)




def check_filename(filename: str) -> bool:
	# chech extention
	if filename.count('.') > 1: return False
	if filename.count('.') == 0:					# no extention
		pattern = r'^[a-zA-Z0-9_\-]+$'
		if re.match(pattern, filename):
			return True
		else:
			return False
		
	if filename.count('.') == 1:						# has extention
		pattern = r'^[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+$'
		if re.match(pattern, filename):
			return True
		else:
			return False



def valid_path(path: str, not_exist_ok=False) -> Path:
	""" Returns resolved path. If 'not_exist_ok' is True then doesn't check existance of path"""
	if path.strip() == '.':
		return Path.cwd()
	path = Path(path).resolve()
	if not path.exists():
		raise ValueError(f'Specified path does not exist: \n{path}')
	return path



def filename2identifier(filename: str, drop_ext=True) -> str:
    """Converts filename into identifier"""
    if drop_ext is True:
        filename = filename.split('.')[0]
    
    filename = filename.replace('-', '_')    
    identifier = re.sub(r'\W+', '', filename)
    if re.match(r'^\d+', identifier):
        identifier = "_" + identifier


    return identifier
	
		 



