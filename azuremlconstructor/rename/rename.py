from pathlib import Path 

from azuremlconstructor._utils import get_settingspy, is_pipe
from azuremlconstructor.init.args_handling import ArgsHandler
from azuremlconstructor import exceptions
from azuremlconstructor import schemas



class RenameHandler:
    def __init__(self,
                 path: Path,
                 new_name: str):
        
        """ 
            Renaming pipe/step means renaming folder, correcting
            `ENVIRONMENT_FILE` in `.env` file 
        """

        self.path = path
        self.old_name = self.get_oldname()
        self.new_name = new_name


    def validate(self):
        if not is_pipe(self.path, self.old_name):
            pipe_name = get_settingspy(self.path)['NAME']
            raise exceptions.PathHasNoThePipelineException(pipe_name=pipe_name,
                                                               path=self.path,
                                                               message=schemas.PathHasNoThePipelineSchema.message)
        self.new_name = ArgsHandler.valid_pipe_name(self.new_name)  # validate new_name


    def get_oldname(self):
        """ returns old name of the pipeline, based on the path """
        return self.path.name


    def rename_dirs(self):
        """ renames pipe dir. Updates self.path if pipe name was changed """

        self.path.rename(self.path.parent / self.new_name)
        self.path = self.path.parent / self.new_name    # update self.path
    

                    
    def edit_dotenv(self) -> bool:
        """ edit .env for new pipe name """    
        dot_env_file = self.path / 'settings' / '.env'
        assert dot_env_file.exists(), f'Doesnt exists: {dot_env_file}'
        lines = []
        found = False

        with dot_env_file.open(mode='r') as file:
            for line in file.readlines():
                if line.startswith('#'):    # comment line
                    lines.append(line)
                    continue
                elif len(line.strip().replace(' ', '')) == 0:   # empty line
                    lines.append(line)
                    continue

                key, value = line.strip().replace(' ', '').split('=')
                if key == 'ENVIRONMENT_FILE':
                    value = f"{self.path / 'settings/conda_dependencies.yml'}"
                    found = True
                value = value.replace("'", '').replace('"', '') # drop ' and "
                line = f"{key} = '{value}'" + '\n'
                lines.append(line)
            
        with dot_env_file.open('w') as file:
            file.writelines(lines)
            print('Done.')
    

    def rename_pipename_settings(self):
        """ change name in the settings.py. Dirercory already renamed. """
        stgs = self.path / 'settings/settings.py'
        assert stgs.exists()
        lines = []
        # read contend, modify and save into list of lines
        with stgs.open(mode='r') as file:
            for line in file.readlines():
                if line.replace(' ', '').startswith('NAME='):
                    key, value = line.split('=')
                    print(line)
                    print('changing..')
                    value = self.new_name
                    lines.append(f"{key} = '{value}'" + '\n')
                else:
                    if not line.endswith('\n'):
                        lines.append(line + '\n')
                    else:
                        lines.append(line)
        # write previous read
        with stgs.open('w') as file:
            file.writelines(lines)



    def start(self):
        self.validate()
        self.rename_dirs()
        self.rename_pipename_settings()
        self.edit_dotenv()
        
