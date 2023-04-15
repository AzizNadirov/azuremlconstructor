# AMLCTOR

## Azure Machine Learning Pipeline Constructor

`amlctor` allows you to create Azure Machine Learning(shortly - `AML`)  [Pipeline](https://learn.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines?view=azureml-api-2). `amlctor` based on the [Azure Machine Learning SDK](https://learn.microsoft.com/en-us/azure/machine-learning/v1/how-to-create-machine-learning-pipelines?view=azureml-api-1&preserve-view=true), and implements main operations of the Pipeline creation. You can create pipelines with AML Steps, which can take DataInputs.
In amlctor pipeline creation consists of 3 steps:

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

