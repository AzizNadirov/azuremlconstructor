from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from amlctor.core import StepSchema
from amlctor.confs.configs import TEMPLATES_DIR, STEP_NAME_MAX, STEP_NAME_MIN, STEP_NAME_KEYWORDS
from amlctor.utils import get_settingspy, is_pipe, check_filename, filename2identifier
from amlctor import exceptions as exceptions
from amlctor import schemas
from amlctor.input import FileInputSchema, PathInputSchema






class StructureApply:
    jinva_env: Environment = Environment(loader=FileSystemLoader(f"{TEMPLATES_DIR}/apply/"))

    def __init__(self, path):
        """ path which contains settings directory """
        assert isinstance(path, Path) and path.is_dir(), f"incorrect dir: {path}"
        self.path = path
        

    def make_step_dirs(self):
        """ 
            Creates step dirs and files based on the `settings.py` file.
        """
        for step in self.settingspy['STEPS']:
            step_path = self.path / step.name
            step_path.mkdir(mode=0o770, exist_ok=True)                 # create dir for pipe step
            self.create_files(step, step_path)          # create files inside step dir


    def create_files(self, step: StepSchema, step_path: Path):
        script_name = self.settingspy['SCRIPT_MODULE_NAME']               # create script.py
        if not script_name.endswith('.py'):
                script_name = script_name + '.py'
        if (step_path / script_name).exists():
            response = input(f"file '{(step_path / script_name)}' already exists. Type- overwrite: o; skip: s; cancel: c: ")
            if response.lower().strip() in ('o', 'overwrite'):
                (step_path / script_name).touch(exist_ok=True)
            elif response.lower().strip() in ('s', 'skip'):
                pass

            elif response.lower().strip() in ('c', 'cancel'):
                raise SystemExit("Cancelled.")
            else:
                raise ValueError(f"Incorrect answer '{response}'. It must be one of [o, s, c]")
            
        # create data_loader.py
        dataloader_name = self.settingspy['DATALOADER_MODULE_NAME'] 
        dataloader_name = self.ext(dataloader_name, True)                 # add .py
        content, keys = StructureApply.create_dataloader_content(step=step)
        
        with (step_path / dataloader_name).open(mode='w+') as dataloader:
            dataloader.write(content)
        # create aml.py
        aml_name = self.settingspy['AML_MODULE_NAME']
        aml_name = self.ext(aml_name, True)
        with (step_path / aml_name).open(mode='w+') as aml:
            aml_t = StructureApply.jinva_env.get_template('aml')
            dataloader_name = self.ext(dataloader_name, yes=False)     # no extention for importing in template
            content = aml_t.render(dataloader_name=dataloader_name, keys=keys)
            aml.write(content)


    
    def ext(self, filename: str, yes=True):
        """ 
            Returns filename with or without '.py extention'.
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
                for filename in data.files:
                    filename_idn = filename2identifier(filename)
                    if first_iter is True:
                        res[filename_idn] = [filename, data.name, get_pandas_reader(filename), 1]
                        first_iter = False
                    else:
                        res[filename_idn] = [filename, data.name, get_pandas_reader(filename), 0]

            elif isinstance(data, PathInputSchema):
                res[data.name] = [-1, data.name, -1, 1]    # pandas method for PathInput = -1
            
            else:
                ValueError(f"InternalError: Unsupported DataInput object: {type(data)}")
        
        content = dataloader_t.render(inputs=res)
        return content, list(res.keys())
    
        

    def start(self):
        self.settingspy = get_settingspy(self.path)
        self.pipe_name: str = self.path.name
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

