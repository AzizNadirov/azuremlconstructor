# aml-constructor

## Azure Machine Learning Pipeline Constructor

`aml-constructor` - or shortly - `azuremlconstructor` allows you to create Azure Machine Learning(shortly - `AML`)  [Pipeline](https://learn.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines?view=azureml-api-2). `azuremlconstructor` based on the [Azure Machine Learning SDK](https://learn.microsoft.com/en-us/azure/machine-learning/v1/how-to-create-machine-learning-pipelines?view=azureml-api-1&preserve-view=true), and implements main operations of the Pipeline creation. You can create pipelines with AML Steps, which can take DataInputs.
In azuremlconstructor pipeline creation consists of 3 steps:

### 0. Preporation

It's highly recommended to create separated folder your pipeline projects. And also, virtual environment(venv) - [article on RealPython](https://realpython.com/python-virtual-environments-a-primer/). You can create separated venv for future AML projects. It's specially useful if you are working with different kinds of libraries: data science oriented, web and so on.

### 1. Pipeline initialisation

Something like project initialisation. You choose pipeline name, directory and credential `.env` file. For storing azuremlconstructor has denv storage - or **EnvBank**. Initialise pipeline as:

```bash
python -m azuremlconstructor init [path] -n myfirstpipe -e denv_name
```

Here `-n` shows pipeline name, `path` - directory in which pipeline will be created - by default = `.`, `-e` - dotenv name. I will talk about denv's a little bit later. After this, in the passed directory will be created named as pipeline passed name.

```directory
myfirstpipe
---|settings/
------|settings.py
------|.amlignore
------|.env
------|conda_dependencies.yml
```

 Inside the directory `settings` directory which contains: `settings.py`, `.amlignore`, `.env` and `conda_dependencies.yml` files. `conda_dependencies.yml` will be used for environment creation on AML side. `.amlignore` something like `.gitignore` but for AML. `.env` is file form of our EnvBank instance. `-e` is optional, if it's skipped, will be created `.env` template with necessary fields, which you have to fill before *running* pipeline.

 **`settings.py`**:

 This module contains all necessary configuractions:

 ```python
from azuremlconstructor.input import FileInputSchema, PathInputSchema
from azuremlconstructor.core import StepSchema

# --------------------------| Module Names |----------------------------
AML_MODULE_NAME: str =       'aml'
SCRIPT_MODULE_NAME: str =    'script'
DATALOADER_MODULE_NAME: str = 'data_loader'



# ---------------------------| General |---------------------------------

NAME = "{{pipe_name}}"
DESCRIPTION = "Your pipeline description"


# ---------------------------| DataInputs |-------------------------------

file = FileInputSchema(
                        name='name', 
                        datastore_name='datastore', 
                        path_on_datastore='', 
                        files = ['file.ext'], 
                        data_reference_name = ''
    )

path = PathInputSchema(
                        name='name', 
                        datastore_name='datastore', 
                        path_on_datastore='',
                        data_reference_name=''
    )
# ---------------------------| Steps |---------------------------------
step1 = StepSchema(
                        name='step_name', 
                        compute_target='compute_name', 
                        input_data=[file, path], 
                        allow_reuse=False
            )
STEPS = [step1, ]

# ---------------------------| extra |---------------------------------

# 'submit' option will apply if set `is_active = True`

EXTRA = {
            'continue_on_step_failure': False,
            'submit': {'is_active': False, 'experiment_name': 'DebugPipeline', 'job_name': NAME, 'tags': None, 'kwargs': None}
}
 ```

Lets look at the variables we have here.

`AML_MODULE_NAME` - initially, pipeline project has 3 main scripts: `dataloader.py` - loads all the DataInputs into the pipeline, `aml.py` - main script of the pipeline, loaded data inputs imported here automaticaly, `script.py` - just empty script for implement your deep logic. You are free for remove this module or add so many as you need, however - the entry point of project is `aml.py`. `AML_MODULE_NAME` is the name of aml.py module. And the same thing for `DATALOADER_MODULE_NAME` and `SCRIPT_MODULE_NAME`.

`NAME` - name of your pipeline.

`DESCRIPTION` - description of the pipeline.

`PathInputSchema` and `FileInputSchema` DataInput of your pipeline. You create instances of the classes and pass into `StepSchema` class. Each `StepSchema` class is abstraction of [`PythonScriptStep`](https://learn.microsoft.com/en-us/python/api/azureml-pipeline-steps/azureml.pipeline.steps.python_script_step.pythonscriptstep?view=azure-ml-py). All steps must be inside `STEPS` list.

#### `EXTRA` options

There are extra - additional options that can be helpfull.

- `continue_on_step_failure` - Indicates whether to continue execution of other steps in the PipelineRun if a step fails; the default is false. If True, only steps that have no dependency on the output of the failed step will continue execution.
  
- `submit` - submit options. Pipeline will be submitted, if `is_active` is `True`.

After filling settings, you have to apply your settings.

### 2. **Apply** Settings

```bash
python -m azuremlconstructor apply <path_to_pipeline>
```

Applying pipeline means - create structure based on the `settings.py` module. For each step will be created directory inside pipeline directory and each directory will contain: `aml.py`, `dataloader.py` and `script.py`.

After applying, your project structure will be like this:

```directory
myfirstpipe
---|settings/
------| settings.py
------| .amlignore
------| .env
------| conda_dependencies.yml
---| step_name/
------| dataloader.py
------| aml.py
------| script.py
---| step2_name/
------| dataloader.py
------| aml.py
------| script.py
```

**Note**: names of the modules setted in the `settings.py` module.

### 3. **Run** Pipeline

bash```
python -m azuremlconstructor run <path_to_pipeline>```

This command will publish your pipeline into your AML. Additionally, can submit according to the `EXTRA.submit` option.

## EnvBank

For work on AML pipeline you have to use your credentials: `workspace_name`, `resource_group`, `subscription_id`, `build_id`, `environment_name` and `tenant_id`. In amltor these variables store as instances of `EnvBank`, which is encrypted jsonlike file. You can create, retrieve or remove `EnvBank` instances(I'll name it as `denv`). In this purpose you've to use `denv` command.

### **Create denv**

You can create denv in 2 ways: pass path of existing `.env` file or in interactive mode - via terminal. In the first case:

```bash
python -m azuremlconstructor denv create -p <path_to_.env file> -n <new_name>
```

Then you'll type new password twise for encryption. After that, denv will save into local storage and you will be able to use it for future pipeline creation.

For create denv in interactive mode, you have to pass `-i` or `--interactive` arg:

```bash
python -m azuremlconstructor denv create -i
```

After that you have to type each asked field and set password.

### Get denv

For retrieve denv use:

```bash
python -m azuremlconstructor denv get -n <name_of_denv>
```

For list all existing denv names add -`-all` argument:

```bash
python -m azuremlconstructor denv get --all
```

**Note**: *for view the denv, you have to type password*.

### Remove denv

For removing denv:

```bash
python -m azuremlconstructor denv rm -n <name_of_denv>
```

## DataInputs

DataInputs can be files or paths from [AML Datastore](https://learn.microsoft.com/en-us/python/api/azureml-core/azureml.core.datastore.datastore?view=azure-ml-py). Whole process is creating [DataReference](https://learn.microsoft.com/en-us/python/api/azureml-core/azureml.data.data_reference.datareference?view=azure-ml-py) object behind the scenes... All inputs will be loaded in the `dataloader.py` and imported into `aml.py` module. Lets look at `azuremlconstructor` DataInputs.

### PathInputSchema

Allows you to create data reference link to any directory inside the datastore. class looks like this:

```python
class PathInputSchema:
    name: str
    datastore_name: str
    path_on_datastore: str
    data_reference_name: str
```

Where: `name` name of your PathInput, this name will be used as variable name for importing. `datastore_name` - Datastore name, `path_on_datastore` - target path related to the Datastore. `data_reference_name` - data reference name for `DataReference` class, optional - if empty, will be used name.

### FileInputSchema

Allows you to mount files from Datastore. Behind the scines, very similar to PathInput, but with *file oriented* additions.

```python
class FileInputSchema:
    name: str
    datastore_name: str
    path_on_datastore: str
    data_reference_name: str
    files: List[str]
```

First 4 fields as previous. `files` - you can list file or files as list, which will be mounted from Datastore. If you want to get one file, pass as string, for more files - list of strings. File inputs will be assigned to variable names - generated  on the base of file name itself. You can use `FileInputSchema.files` *dict notation*, which allows you pass `{'file_name.extention': 'variable_name', 'file_name2.extention': 'variable_name2', ...}` for map files with variable names to use. Remember that, variable names must be unique in the scope of step. When you pass multiple filename, they must be on the same path.

**Supported file types**: `azuremlconstructor` uses `pandas` `pandas.read_...` methods for read the mounted files. At the moment, suported file types:

```directory
csv, parquet, excell sheet, json
```

Slugged file names will be used as variable names for importing files.

## Other commands

### Update

You can update project according to the `settings.py`. Updates  will affect whole project if passed `--overwrite`. Otherwise, user have to choose what to do with already existing modules - `overwrite`, `skeep` or `cancel` updating. It can be useful when you maked some changes into `settings.py` and don't want to overwrite whole pipeline structure by scratch, in this case you can use `update`:

```bash
python -m azuremlconstructor update <path_to_pipe> --overwrite [Optional]
```

### Rename

```bash
python -m azuremlconstructor rename <path_to_pipe> -n <new_name>
```

Renames pipeline into `new_name`. Renaming pipeline means: rename pipeline project directory, change `NAME` variable in `settings.py` and edit `ENVIRONMENT_FILE` in the `.env` file.

### Some usefull utils

`azuremlconstructor.utils` module has a banch of usefull tools, that can be usefull.
    - `utils.upload_data(datastore_name: str, files: List[str], target_path: str=".")` - uploads file(s) to the blob;
    - *recursive read_concat* functions: `utils.read_concat_csvfiles: List[str], return_types: bool=False, sep: str = ','`, `utils.read_concat_parquet(files: List[str], return_types: bool=False, engine: Literal['fastparquet', 'pyarrow'] = 'fastparquet')`, `utils.recursive_glob_list(folders: List[str], file_ext: str='parquet')`. Each function has doc
