from typing import List, Union, Callable
from dataclasses import dataclass

import pandas as pd

from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential


from azureml.core import Workspace, Datastore
from azureml.data.datapath import DataPath, DataPathComputeBinding
from azureml.core.authentication import InteractiveLoginAuthentication

from amlctor.denv.dot_env_loader import get_env

from amlctor.exceptions import IncorrectTypeArgumentException
from amlctor.schemas import IncorrectArgumentTypeSchema


env = get_env()




class FileInput:
    """ Adds file from the datastore """
    def __init__(self, name: str, 
                filename: Union[list, str],
                datastore_name: str, 
                path_on_datasore: str, 
                data_reference_name: str = ''):
        """
            name:                   name your input instance
            filename:               file name(s) that should be given
            datastore_name:         datastore name that contains file(s)
            path_on_datasore:       path to the file from the datastore
            data_reference_name:    data reference name, if not passed 'name' will be used 
        """
        
        if data_reference_name == '':
            data_reference_name = name
            
        e = env
        compute_binding = DataPathComputeBinding(mode="mount")
        self.data_reference_name = data_reference_name

        self.workspace = self.__get_workspace(e)
        self.data_store = Datastore.get(self.workspace, datastore_name)
        
        if isinstance(filename, str):
            path_to = DataPath(datastore=self.data_store, path_on_datastore=path_on_datasore)
            self.data = [path_to.create_data_reference(data_reference_name=data_reference_name, 
                                                       datapath_compute_binding=compute_binding)]
            self.name = name
            self.filenames = filename
            self.validator(name)

        elif isinstance(filename, (list, tuple, set)):
            self.data = []
            for fname in filename:
                path_to = DataPath(datastore=self.data_store, 
                                   path_on_datastore=f"{path_on_datasore}/{fname}")
                
                self.data.append(path_to.create_data_reference(data_reference_name=fname,                                                     datapath_compute_binding=compute_binding))
        else:
            raise ValueError(f"Incorrect data type for filename: {type(filename)}. Should be one of: str, list, tuple or set")


    def __get_workspace(self, e):
        interactive_auth = InteractiveLoginAuthentication(tenant_id=e.tenant_id)
        workspace = Workspace.get(
            name=e.workspace_name,
            subscription_id=e.subscription_id,
            resource_group=e.resource_group,
            auth=interactive_auth
        )
        return workspace


    def validator(self, name):
        if not (isinstance(name, str) and name.isidentifier()):
            raise ValueError(f"Incorrect value for 'name': {name}")
        



class PathInput:
    """ Sone path from datastore """
    def __init__(self, name: str, datastore_name: str, path_on_datasore: str):
        e = env
        self.workspace = self.__get_workspace(e)
        self.datastore = Datastore.get(self.workspace, datastore_name)
        self.path = path_on_datasore
        self.name = name

    def __get_workspace(self, e):
        interactive_auth = InteractiveLoginAuthentication(tenant_id=e.tenant_id)
        workspace = Workspace.get(
            name=e.workspace_name,
            subscription_id=e.subscription_id,
            resource_group=e.resource_group,
            auth=interactive_auth
        )
        return workspace
    

    def upload(self, filenames: list, overwrite=True, show_progress=True):
        """ 
            Uploads files into the path. Files from filenames should be exist
        """
        if isinstance(filenames, str):          # if passed as string single file name
            filenames = [filenames, ]           # then convert to the list
        self.data_store.upload_files(files=filenames,
                                     target_path=self.path,
                                     overwrite=overwrite,
                                     show_progress=show_progress)



class GetBlobFile:
    """ Downloads file(s) from the blob storage """
    def __init__(self, 
                 storage_account_name: str,
                 container_name: str,
                 blob_name: Union[str, List[str]],
                 download_filename: Union[str, List[str]]):
        """ 
            storage_account_name:   name of storage account;
            container_name:         name of the container
            blob_name:              blob name - relational path of file from from the container.
                                    If passed string - download the file, if list - download all passed 
                                    files from from the container.
            download_filename:      new name for file will be downloaded. If blob name contains multiple files,
                                    pass list of new names. If `blob_name` has multiple files, but `download_filename`
                                    is single name, new names will be named as `{download_filename}_i` where i = 1,2,..

        """

        self.account = storage_account_name
        self.container = container_name
        self.blob_name = blob_name
        self.download_filename = download_filename

        self.__credential = DefaultAzureCredential()



    def validate(self) -> None:
        if not isinstance(self.account, str):
            raise IncorrectTypeArgumentException(valid_type=str, actually_is=type(self.account),
                                                 message=IncorrectArgumentTypeSchema.message)
        elif not isinstance(self.container, str):
            raise IncorrectTypeArgumentException(valid_type=str, actually_is=type(self.container),
                                                 message=IncorrectArgumentTypeSchema.message)
        elif not isinstance(self.blob_name, str, list, tuple):
            raise IncorrectTypeArgumentException(valid_type=(str, list, tuple), actually_is=type(self.blob_name),
                                                 message=IncorrectArgumentTypeSchema.message)
        elif not isinstance(self.download_filename, str, list, tuple):
            raise IncorrectTypeArgumentException(valid_type=(str, list, tuple), actually_is=type(self.download_filename),
                                                 message=IncorrectArgumentTypeSchema.message)
        
        # blob name = single; download_filename == many
        elif GetBlobFile.__is_single(self.blob_name) and not GetBlobFile.__is_single(self.download_filename):
                raise ValueError(
                    f"You try to download one file and save as multiple names. In this case 'download_filename'"
                        "must be string or 1 item length list or tuple")
        
        # many & many and lens different
        elif not GetBlobFile.__is_single(self.blob_name) and not GetBlobFile.__is_single(self.download_filename) and len(self.blob_name != self.download_filename):
            raise ValueError(f"Dismatch lengths of 'download_filename' and 'blob_name': {len(self.download_filename)} and {self.blob_name}")


    @staticmethod
    def __is_single(inp: Union[str, list, tuple]) -> bool:
            if isinstance(inp, str): return True
            if isinstance(inp, list, tuple) and len(inp) == 1: return True
            else: return False


    @staticmethod
    def __single2str(inp) -> str:
            if isinstance(inp, list, tuple) and len(inp) == 1:
                return inp[0]
            if isinstance(inp, str):
                return inp
            else:
                raise TypeError(f"Multiple items in sequence, disable to convert to string.")


    def get_client(self) -> BlobServiceClient:
        blob_service_client_instance = BlobServiceClient(account_url=f"https://{self.account}.blob.core.windows.net", # TODO: try-except
                                                         credential=self.__credential)
        blob_client_instance = blob_service_client_instance.get_blob_client(self.container, self.blob_name, snapshot=None)
        return blob_client_instance



    def download_files(self, validate: bool=True) -> None:
        """
            Downloads files. 
            validate: internally, validation is True, for separated using recommended using `validate=True`
        """
        if validate is True:
            self.validate()

        client = self.get_client()
        # when blob_name is single file
        if GetBlobFile.__is_single(self.blob_name):
            blob_client_instance = client.get_blob_client(self.container, self.blob_name, snapshot=None)
            download_filename = GetBlobFile.__single2str(self.download_filename)              
            with open(download_filename, "wb") as my_blob:
                blob_data = blob_client_instance.download_blob()
                blob_data.readinto(my_blob)

        # when blob_name is multiple file
        elif not GetBlobFile.__is_single(self.blob_name):
            # when download_filename is single file
            if GetBlobFile.__is_single(self.download_filename):
                download_filename = GetBlobFile.__single2str(self.download_filename)
                for i, b_name in enumerate(self.blob_name, start=1):
                    blob_client_instance = client.get_blob_client(self.container, b_name, snapshot=None)
                    with open(f"{download_filename}_{i}", "wb") as my_blob:
                        blob_data = blob_client_instance.download_blob()
                        blob_data.readinto(my_blob)

            else:   # when download_filename is multiple file - lenghts are equal
                for new_name, b_name in zip(self.download_filename, self.blob_name):
                    blob_client_instance = client.get_blob_client(self.container, b_name, snapshot=None)
                    with open(new_name, "wb") as my_blob:
                        blob_data = blob_client_instance.download_blob()
                        blob_data.readinto(my_blob)
            

    @staticmethod
    def __check_exts_and_get_reader(file_name: str) -> Union[Callable, bool]:
        valid_exts = {'csv': pd.read_csv, 
                      'parquet': pd.read_parquet, 
                      'json': pd.read_json, 
                      'xls': pd.read_excel, 'xlsx': pd.read_excel}
        ext = file_name.split('.')[-1]      # take extention of the file

        if not ext in valid_exts.keys():
            return False
        else:
            return valid_exts[ext]  # return pd.read_xxx function



    def download_and_read(self, validate: bool=True, extra_args: dict=None) -> Union[List[pd.DataFrame], pd.DataFrame]:
        """ 
            Download and read files as pandas.DataFrame. Supported file types:
                [csv, parquet, json, excel]

            validate:   internally, validation is True, for separated using recommended using `validate=True`
            extra_args: extra arguments that will passed into pd.read_xxx function, after file name
                        as: `pd.read_xxx(filename, **extra_args)` 
        """
        # check for ability of read as pandas dataframe
        if not GetBlobFile.__is_single(self.download_filename):
            dfs = []
            for filename in self.download_filename: 
                reader = GetBlobFile.__check_exts_and_get_reader(filename)
                if not reader:
                    raise ValueError(f"Invalid file for reading: {filename}")
                
                # start downloading:
                self.download_files(validate=validate)
                # read downloaded files
                if extra_args:  df = reader(filename, **extra_args)
                else:           df = reader(filename)
                dfs.append(df)

            return dfs
            
        if GetBlobFile.__is_single(self.download_filename):
            download_filename = GetBlobFile.__single2str(self.download_filename)
            reader = GetBlobFile.__check_exts_and_get_reader(download_filename)
            if not reader:
                raise ValueError(f"Invalid file for reading: {download_filename}")
            
            # start downloading:
            self.download_files(validate=validate)
            # read downloaded files
            if extra_args:  df = reader(download_filename, **extra_args)
            else:           df = reader(download_filename)

            return df



@dataclass(frozen=True)
class FileInputSchema:
    name: str
    datastore_name: str
    path_on_datastore: str
    data_reference_name: str
    files: List[str]


@dataclass(frozen=True)
class PathInputSchema:
    name: str
    datastore_name: str
    path_on_datastore: str
    data_reference_name: str
