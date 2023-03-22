from pathlib import Path 

from amlctor.utils import get_settingspy_module, is_pipe
from amlctor.init.args_handling import ArgsHandler



class RenameHandler:
    def __init__(self,
                 path: Path,
                 old_name: str,
                 new_name: str,
                 is_step: bool):
        
        """ 
            Renaming pipe/step means renaming folder, correcting
            `ENVIRONMENT_FILE` in `.env` file 
        """

        self.path = path
        self.old_name = old_name
        self.new_name = new_name
        self.is_step = is_step


    def validate(self):
        if not self.is_step is True:
            if not is_pipe(self.path, self.old_name):
                raise ValueError(f"Passed path doesn't contain pipeline: '{self.path}'")
            
        if self.is_step is True:
            if not is_pipe(self.path, self.old_name, is_step=True):
                raise ValueError(f"Passed path doesn't contain pipeline: '{self.path}'")
        
        self.new_name = ArgsHandler.valid_pipe_name(self.new_name)  # validate new_name


    def rename_dirs(self):
        """ renames pipe or step dirs. Updates self.path if pipe name was changed """
        if self.is_pipe is True:
            self.path.rename(self.new_name)
            self.path = self.path.parent / self.new_name    # update self.path
        
        if self.is_step is True:
            for d in self.path.iterdir():
                if d.is_dir() and d.name == self.old_name:
                    d.rename(self.new_name)

                    
    def edit_dotenv(self) -> bool:
        dot_env_file = self.path / 'settings' / '.env'
        lines = []
        found = False

        with dot_env_file.open(mode='w+') as file:
            for line in file.readlines():
                line = line.strip().replace(' ', '')
                key, value = line.split('=')
                if key == 'ENVIRONMENT_FILE':
                    value = value.replace(self.old_name, self.new_name)
                    found = True
                line = f"{key} = {value}"
                lines.append(line)
            
            file.writelines(lines)
        
        return found 


    def start(self):
        self.validate()
        self.rename_dirs()
        found = self.edit_dotenv()
        
