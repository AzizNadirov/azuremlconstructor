from importlib.util import spec_from_file_location
from pathlib import Path
import re
from typing import List, Tuple




def ext(filename: str, yes=True):
        """ 
            Returns filename with or without '.py` extention.
            yes: if True then add '.py', else drop out.
        """
        filename = filename.strip()     # just 4 fun

        if filename.endswith('.py'): # has extention
            if yes is True:
                return filename
            else:
                return filename.split('.')[0]
        else:                           # has no extention
            if yes is True:
                return filename + '.py'
            else:
                return filename


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



def is_step(path: Path, stdout: bool = True) -> bool:
	""" 
		Check if path is a step 
		Params:
			path: path to the step
			stdout: if True, print result
	"""
	pipe_path = path.parent
	settings = get_settingspy(pipe_path)
	# add extention
	aml_name = ext(settings['AML_MODULE_NAME'])
	script_name = ext(settings['SCRIPT_MODULE_NAME'])
	dataloader_name = ext(settings['DATALOADER_MODULE_NAME'])
	
	if not path.exists():	return False
	# check if parent is pipeline
	pipe_path = path.parent
	settings = get_settingspy(pipe_path)
	if stdout:
		if (path / script_name).exists() and \
			(path / aml_name).exists() and \
			(path / dataloader_name).exists():
			return True
		return False
	else:	# the same thing, but with prints
		step_name = path.name.split('.')[0]
		if (path / script_name).exists():
			if (path /aml_name).exists():
				if (path / dataloader_name).exists():
					print(f"\t{step_name} is correct step: OK")
					return True
				else:
					print(f"\t{path / dataloader_name} doesn't exist")
					return False
			else:
				print(f"\t{path / aml_name} doesn't exist")
				return False
		else:
			print(f"\t{path / script_name} doesn't exist")
			return False
		




def has_step(path: Path, step_name: str) -> bool:
	""" check if path has the step with `step_name` 
		Params:
			path: path of pipeline
			step_name: name of the step
	"""
	return (path / step_name).exists() and is_step(path=path/step_name)




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
	
		 

def get_not_applied_steps(path: Path) -> Tuple[str]:
	"""  
		Check steps. Returns not applied step names.
		Params:
			path: Path - path of pipeline
		returns: Tuple[str] - tuple of stepnames that are not implemented 

	"""
	unapplieds = []
	settings = get_settingspy(path)
	steps = settings['STEPS'].copy()
	for step in steps:
		if not has_step(path, step.name):
			unapplieds.append(step.name)

	return tuple(unapplieds)





