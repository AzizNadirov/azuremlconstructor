# AMLCTOR

## Azure Machine Learning Pipeline Constructor

`amlctor` allows you to create Azure Machine Learning(shortly - `AML`)  [Pipeline](https://learn.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines?view=azureml-api-2). `amlctor` based on the [Azure Machine Learning SDK](https://learn.microsoft.com/en-us/azure/machine-learning/v1/how-to-create-machine-learning-pipelines?view=azureml-api-1&preserve-view=true), and implements main operations of the Pipeline creation. You can create pipelines with AML Steps, which can take DataInputs.
In amlctor pipeline creation consists of 3 steps:

### 0. Preporation

It's highly recommended to create separated folder your pipeline projects. And also, virtual environment(venv). You can create separated venv for future AML projects. It's specially useful if you are working with different kinds of libraries: data science oriented, web and so on.

### 1. Pipeline initialisation

Something like project initialisation. You choose pipeline name, directory and credential `.env` file. For storing amlctor has denv storage - or **EnvBank**. Initialise pipeline as:

```bash
python -m amlctor init -n myfirstpipe -p . -e denv_name
```

Here `-n` shows pipeline name, `-p` - directory in which pipeline will be created, `-e` - dotenv name. I will talk about denv's a little bit later. After this, in the passed directory will be created named as pipeline passed name.

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
from amlctor.input import FileInputSchema, PathInputSchema
from amlctor.core import StepSchema

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


EXTRA = {
            'continue_on_step_failure': False,
}
 ```

Lets look at the variables we have here.

`AML_MODULE_NAME` - initially, pipeline project has 3 main scripts: `dataloader.py` - loads all the DataInputs into the pipeline, `aml.py` - main script of the pipeline, loaded data inputs imported here automaticaly, `script.py` - just empty script for implement your deep logic. You are free for remove this module or add so many as you need, however - the entry point of project is `aml.py`. `AML_MODULE_NAME` is the name of aml.py module. And the same thing for `DATALOADER_MODULE_NAME` and `SCRIPT_MODULE_NAME`.

`NAME` - name of your pipeline.

`DESCRIPTION` - description of the pipeline.

`PathInputSchema` and `FileInputSchema` DataInput of your pipeline. You create instances of the classes and pass into `StepSchema` class. Each `StepSchema` class is abstraction of [`PythonScriptStep`](https://learn.microsoft.com/en-us/python/api/azureml-pipeline-steps/azureml.pipeline.steps.python_script_step.pythonscriptstep?view=azure-ml-py). All steps must be inside `STEPS` list.

After filling settings, you have to apply your settings.

### 2. **Apply** Settings

```bash
python -m amlctor apply -p <path_to_pipeline>
```

Applying pipeline means - create structure based on the `settings.py` module. For each step will be created directory inside pipeline directory and each directory will contain: `aml.py`, `dataloader.py` and `script.py`. **Note**: names of the modules setted in the `settings.py` module.

### 3. **Run** Pipeline

```bash
python -m amlctor run -p <path_to_pipeline>
```

This command will publish your pipeline into your AML.

## EnvBank

For work on AML pipeline you have to use your credentials: `workspace_name`, `resource_group`, `subscription_id`, `build_id`, `environment_name` and `tenant_id`. In amltor these variables store as instances of `EnvBank`, which is encrypted jsonlike file. You can create, retrieve or remove `EnvBank` instances(I'll name it as `denv`). In this purpose you've to use `denv` command.

### **Create denv**

You can create denv in 2 ways: pass path of existing `.env` file or in interactive mode - via terminal. In the first case:

```bash
python -m amlctor denv create -p <path_to_.env file> -n <new_name>
```

Then you'll type new password twise for encryption. After that, denv will save into local storage and you will be able to use it for future pipeline creation.

For create denv in interactive mode, you have to pass `-i` or `--interactive` arg:

```bash
python -m amlctor denv create -i
```

After that you have to type each asked field and set password.

### Get denv

For retrieve denv use:

```bash
python -m amlctor denv get -n <name_of_denv>
```

For list all existing denv names add -`-all` argument:

```bash
python -m amlctor denv get --all
```

**Note**: *for view the denv, you have to type password*.

### Remove denv

For removing denv:

```bash
python -m amlctor denv rm -n <name_of_denv>
```

## DataInputs

DataInputs can be files or paths from [AML Datastore](https://learn.microsoft.com/en-us/python/api/azureml-core/azureml.core.datastore.datastore?view=azure-ml-py). Whole process is creating [DataReference](https://learn.microsoft.com/en-us/python/api/azureml-core/azureml.data.data_reference.datareference?view=azure-ml-py) object behind the scenes... All inputs will be loaded in the `dataloader.py` and imported into `aml.py` module. Lets look at `amlctor` DataInputs.

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

First 4 fields as previous. `files` - you can list file or files as list, which will be mounted from Datastore. If you want to get one file, pass as string, for more files - list of strings. When you pass multiple filename, they must be on the same path.

**Supported file types**: `amlctor` uses `pandas` read methods for read the mounted files. At the moment, suported file types:

```directory
csv, parquet, excell sheet, json
```

Slugged file names will be used as variable names for importing files.

## Other commands

### Update

You can update `dataloader` according to the `settings.py` module. It can be useful when you maked some changes into `settings.py` and don't want to overwrite whole pipeline structure by scratch, in this case you can use `update`:

```bash
python -m amlctor update -p <path_to_pipe> -s step_name [Optional]
```

`step_name` argument is optional, if not passed, updating will apply for all steps, otherwise - only for passed step.

### Rename

```bash
python -m amlctor rename -p <path_to_pipe> -n <new_name>
```

Renames pipeline into `new_name`. Renaming pipeline means: rename pipeline project directory, change `NAME` variable in `settings.py` and edit `ENVIRONMENT_FILE` in the `.env` file.
