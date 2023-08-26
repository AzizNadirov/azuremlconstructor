import glob
from typing import List, Union, Literal

import pandas as pd
from azureml.core import Run, Datastore



def read_concat_parquet(files: List[str], return_types: bool=False, engine: Literal['fastparquet', 'pyarrow'] = 'fastparquet'):
    """ Takes a list of .parquet filess and returns a single dataframe """
    assert engine in ('fastparquet', 'pyarrow'), "Available engines: fastparquet, pyarrow"
    dfs = [pd.read_parquet(f,engine=engine) for f in files]
    df = pd.concat(dfs)
    if return_types:
        dtypes_df = pd.concat([df.dtypes for df in dfs], axis=1).T
        return df, dtypes_df
    else:
        return df


        
def read_concat_csv(files: List[str], return_types: bool=False, sep: str = ','):
    """ Takes a list of .csv files and returns a single dataframe """
    li = []
    for filename in files:
        df = pd.read_csv(filename, index_col = None, header = 0, sep = sep)
        li.append(df)

    frame = pd.concat(li, axis=0, ignore_index=True)
    return frame


def read_concat_excel(files: List[str], return_types: bool=False):
    """ Takes a list of .xlsx files and returns a single dataframe """
    dfs = [pd.read_excel(f) for f in files]
    df = pd.concat(dfs)
    if return_types:
        dtypes_df = pd.concat([df.dtypes for df in dfs], axis=1).T
        return df, dtypes_df
    else:
        return df

def recursive_glob_list(folders: List[str], file_ext: str='parquet'):
    """ Takes a list of folders and returns a list of files recursively """
    files = []
    for f in folders:
        files += glob.glob(f"{f}/**/*.{file_ext}", recursive=True)
    return files


def upload_data(datastore_name: str, files: List[str], target_path: str="."):
    """ Uploads a list of files to a datastore 
        Params:
            datastore_name: name of the datastore to upload to
            files: list of files to upload
            target_path: path to upload files - relative to datastore
    """
    run = Run.get_context()

    datastore = Datastore.get(run.experiment.workspace, datastore_name)
    datastore.upload_files(
        files,
        target_path=target_path,
        overwrite=True,
        show_progress=True,
    )
