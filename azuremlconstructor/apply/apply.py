from pathlib import Path
from typing import List, Literal

from jinja2 import Environment, FileSystemLoader

from azuremlconstructor.core import StepSchema
from azuremlconstructor.confs.configs import TEMPLATES_DIR, STEP_NAME_MAX, STEP_NAME_MIN, STEP_NAME_KEYWORDS
from azuremlconstructor._utils import get_settingspy, is_pipe, check_filename, filename2identifier
from azuremlconstructor import exceptions as exceptions
from azuremlconstructor import schemas
from azuremlconstructor.input import FileInputSchema, PathInputSchema






class StructureApply:
    jinva_env: Environment = Environment(loader=FileSystemLoader(f"{TEMPLATES_DIR}/apply/"))

    def __init__(self, path):
        """ path which contains settings directory """
        assert isinstance(path, Path) and path.is_dir(), f"incorrect dir: {path}"
        self.path = path
        self.settingspy = get_settingspy(self.path)
        self.pipe_name: str = self.path.name
        

    def make_step_dirs(self, for_steps: list=None, overwrite: bool=False):
        """ 
            Creates step dirs and files based on the `settings.py` file.
            Params:
                for_steps: List[str] - if passes, creates only for these steps
                overwrite: bool - if True, overwrites files
        """
        if not for_steps:
            for step in self.settingspy['STEPS']:
                step_path = self.path / step.name
                step_path.mkdir(mode=0o770, exist_ok=True)                 # create dir for pipe step
                self.create_files(step, step_path, overwrite)          # create files inside step dir
        else:
            for step in self.settingspy['STEPS']:           # do only for passed steps
                if not step.name in for_steps:
                    continue
                step_path = self.path / step.name
                step_path.mkdir(mode=0o770, exist_ok=True)                 # create dir for pipe step
                self.create_files(step, step_path, overwrite)          # create files inside step dir


    def create_files(self, step: StepSchema, step_path: Path, overwrite: bool):
        """ creates modules """
        def create(kind: Literal['aml', 'script', 'dataloader']) -> None:
            if kind == 'aml':
                # (step_path / self.settingspy['AML_MODULE_NAME']).touch(exist_ok=True)
                aml_name = self.settingspy['AML_MODULE_NAME']
                aml_name = self.ext(aml_name, True)
                with (step_path / aml_name).open(mode='w+') as aml:
                    aml_t = StructureApply.jinva_env.get_template('aml')
                    dataloader_name = self.ext(self.settingspy['DATALOADER_MODULE_NAME'], yes=False)     # no extention for importing in template
                    _, keys = StructureApply.create_dataloader_content(step=step)
                    content = aml_t.render(dataloader_name=dataloader_name, keys=keys)
                    aml.write(content)
                    
            elif kind == 'dataloader':
                # (step_path / self.settingspy['DATALOADER_MODULE_NAME']).touch(exist_ok=True)
                dataloader_name = self.settingspy['DATALOADER_MODULE_NAME'] 
                dataloader_name = self.ext(dataloader_name, True)                 # add .py
                content, keys = StructureApply.create_dataloader_content(step=step)
                with (step_path / dataloader_name).open(mode='w+') as dataloader:
                    dataloader.write(content)

            elif kind == 'script':
                # (step_path / self.settingspy['SCRIPT_MODULE_NAME']).touch(exist_ok=True)
                script_name = self.settingspy['SCRIPT_MODULE_NAME'] 
                script_name = self.ext(script_name, True)
                script_t = StructureApply.jinva_env.get_template('script')
                content = script_t.render()
                with (step_path / script_name).open(mode='w+') as script:
                    script.write(content)


        modules = {'script':    self.settingspy['SCRIPT_MODULE_NAME'], 
                   'aml':       self.settingspy['AML_MODULE_NAME'], 
                   'dataloader':self.settingspy['DATALOADER_MODULE_NAME']}
        
        
        if overwrite is False:
            for kind, file_name in modules.items():
                file_name = self.ext(file_name, True) 
                if (step_path / file_name).exists():
                    response = input(f"File '{(step_path / file_name)}' already exists. \nType- overwrite: [o]; skip: [s]; cancel: [c]: ")
                    if response.lower().strip() in ('o', 'overwrite'):
                        (step_path / file_name).touch(exist_ok=True)
                        create(kind=kind)
                    elif response.lower().strip() in ('s', 'skip'):
                        continue
                    elif response.lower().strip() in ('c', 'cancel'):
                        raise SystemExit("Cancelled.")
                    else:
                        raise ValueError(f"Incorrect answer '{response}'. It must be one of [o, s, c]")
                else:
                    (step_path / file_name).touch(exist_ok=True)
        else:
            # create data_loader.py
            create(kind='dataloader')
            # create aml.py
            create(kind='aml')
            # create script.py
            create(kind='script')
            


    
    def ext(self, filename: str, yes=True):
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




    @staticmethod
    def create_dataloader_content(step: StepSchema):
        """ Returns content for dataoaders.py and input names """

        def get_pandas_reader(filename: str):
            """ returns pandas reader method name for filename extention """          
            if filename.endswith('.parquet'):
                return "read_parquet"
            elif filename.endswith(".csv"):
                return "read_csv"
            elif filename.endswith(".xls") or filename.endswith(".xlsx"):
                return "read_excel"
            elif filename.endswith(".json"):
                return "read_json"
            else:
                raise ValueError(f"Unsupported file: {filename}. Supports: parquet, csv, excel, json")

        dataloader_t = StructureApply.jinva_env.get_template('data_loaders')

        res = {}
        data_list = step.input_data     # list of FileInput objects
        # template api: input_name: [filename, data_name, method_name, add_to_argparse]
        # PathInput doesn't have files, so 'filename' and 'method_name' = -1
        for data in data_list:
            if isinstance(data, FileInputSchema):
                first_iter = True
                # data.files == ['file.csv', 'file2.parquet', ...]:
                if isinstance(data.files, (list, tuple)):
                    for filename in data.files:
                        filename_idn = filename2identifier(filename)
                        if first_iter is True:
                            res[filename_idn] = [filename, data.name, get_pandas_reader(filename), 1]
                            first_iter = False
                        else:
                            res[filename_idn] = [filename, data.name, get_pandas_reader(filename), 0]

                # data.files == 'file.csv':
                elif isinstance(data.files, str):
                    filename = data.files
                    filename_idn = filename2identifier(filename)
                    res[filename_idn] = [filename, data.name, get_pandas_reader(filename), 1]

                # data.files == {'file.ext': 'var_name', 'file2.ext': 'var_name2', ...}
                elif isinstance(data.files, dict):
                    # validate var_names - must be unique:
                    if len(data.files.values()) != len(set(list(data.files.values()))):
                        raise ValueError(f"Varable names must be unique: {list(data.files.values())}")
                    for var_name in data.files.values():
                        if not var_name.isidentifier():
                            raise ValueError(f"Invalid variable name: {var_name}")
                    
                    for filename, var_name in data.files.items():
                        filename_idn = filename2identifier(filename)
                        # validate var_name with prev keys:
                        if var_name in res.keys():
                            raise ValueError(f"Varable name intersects with other variables, please rename it or use dict file - variable_name notation. Variable: '{var_name}' Variables: {list(res.keys())}")
                        else:
                            res[var_name] = [filename, data.name, get_pandas_reader(filename), 1]
                else:
                    raise ValueError(f"Got invalid FileInput.files of type: {type(data.files)} with value: {data.files}")
            

            elif isinstance(data, PathInputSchema):
                res[data.name] = [-1, data.name, -1, 1]    # pandas method for PathInput = -1
            
            else:
                ValueError(f"InternalError: Unsupported DataInput object: {type(data)}")
        
        content = dataloader_t.render(inputs=res)
        return content, list(res.keys())
    
        
    def start(self):
        self.make_step_dirs()



class ApplyHandler:

    def __init__(self, path: Path):
        self.path = path
        self.check_path()


    def check_path(self):
        if not is_pipe(self.path):
            raise exceptions.PathHasNoPipelineException(path =      self.path, 
                                                        message =   schemas.PathHasNoPipelineSchema.message)
        

    def validate(self):
        MAX_LEN = 128
        settingspy = get_settingspy(self.path)
        steps = settingspy['STEPS']
        for step in steps:

            if not isinstance(step.name, str):
                raise exceptions.IncorrectTypeArgumentException(valid_type=str,
                                                                actually_is=type(name),
                                                                message=schemas.IncorrectArgumentTypeSchema.message)
            self.name = self.name.strip()
            name = self.name

            if not name.isidentifier():
                raise exceptions.IncorrectStepNameException(step_name = name,
                                                            message =   schemas.IncorrectStepNameSchema.IsNotIdentifier)
            elif len(name) < STEP_NAME_MIN:
                raise exceptions.IncorrectStepNameException(step_name = name,
                                                            message =   schemas.IncorrectStepNameSchema.LowMin)
            elif len(name) > STEP_NAME_MAX:
                raise exceptions.IncorrectStepNameException(step_name = name,
                                                            message =   schemas.IncorrectStepNameSchema.UpMax)
            elif name in STEP_NAME_KEYWORDS:
                raise exceptions.IncorrectStepNameException(step_name = name,
                                                            message =   schemas.IncorrectStepNameSchema.IsKeyWord)
        # check if steps have same names:
        tmp_steplst = []
        for step in steps:
            if step.name in tmp_steplst:
                raise ValueError(f"Dublicate step name: '{step.name}'. Step names must be unique!")
            else:
                tmp_steplst.append(step.name)
            
        # validate files in steps
        for step in steps:
            for inp in step.input_data:
                if isinstance(inp, FileInputSchema):
                    for filename in inp.files:
                        if check_filename(filename=filename) is False:
                            raise exceptions.IncorrectFileNameException(
                                message=schemas.IncorrectFileNameSchema.message,
                                filename=filename)
        # validate data input names for uniqueness
        for step in steps:
            tmp_datainputlst = []
            for inp in step.input_data:
                if inp.name in tmp_datainputlst:
                    raise ValueError(f"Dublicate DataInput name: '{inp.name}'. Input names of the step must be unique!")
                else:
                    tmp_datainputlst.apend(inp.name)



    def start(self):
        StructureApply(path=self.path).start()      # start apply strukture builder

