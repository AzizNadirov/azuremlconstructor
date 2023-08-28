from typing import List, Dict
from dataclasses import dataclass

import pandas as pd

from azureml.core import Workspace, Datastore
from azureml.data.datapath import DataPath, DataPathComputeBinding
from azureml.core.authentication import InteractiveLoginAuthentication

from azuremlconstructor.denv.dot_env_loader import get_env

from azuremlconstructor._utils import filename2identifier




class FileInput:
    """ Adds file from the datastore """
    def __init__(self, name: str, 
                filename: list | tuple | str | dict,
                datastore_name: str, 
                path_on_datasore: str, 
                denv_path: str,
                data_reference_name: str = ''):
        """
            name:                   name your input instance
            filename:               file name(s) that should be given
            datastore_name:         datastore name that contains file(s)
            path_on_datasore:       path to the file from the datastore
            data_reference_name:    data reference name, if not passed 'name' will be used 
        """

        self.name = name
        self.filenames = filename
        self.validate()

        if data_reference_name == '':
            data_reference_name = name
            
        e = get_env(pipe_path=denv_path)
        compute_binding = DataPathComputeBinding(mode="mount")
        self.data_reference_name = data_reference_name

        self.workspace = self.__get_workspace(e)
        self.data_store = Datastore.get(self.workspace, datastore_name)
        
        path_to = DataPath(datastore=self.data_store, path_on_datastore=path_on_datasore)
        self.data = path_to.create_data_reference(data_reference_name=data_reference_name, 
                                                    datapath_compute_binding=compute_binding)


    def __get_workspace(self, e):
        interactive_auth = InteractiveLoginAuthentication(tenant_id=e.TENANT_ID)
        workspace = Workspace.get(
            name=e.WORKSPACE_NAME,
            subscription_id=e.SUBSCRIPTION_ID,
            resource_group=e.RESOURCE_GROUP,
            auth=interactive_auth
        )
        return workspace


    def validate(self)-> bool:
        # name
        if not (isinstance(self.name, str) and self.name.isidentifier()):
            raise ValueError(f"Incorrect value for 'name': {self.name}")
        # filenames
        if not isinstance(self.filenames, (list, tuple, str, dict)):
            raise ValueError(f"Incorrect data type for filename:" 
                             "{type(filename)}. Should be one of: str, list, tuple or dict")
        return True
        
    
    def __str__(self):
        return f"FileInput {self.name}:{self.data_store}|{self.filenames}"
        


class PathInput:
    """ Sone path from datastore """
    def __init__(self, name: str, datastore_name: str, path_on_datasore: str, denv_path: str):
        e = get_env(pipe_path=denv_path)
        self.workspace = self.__get_workspace(e)
        self.datastore = Datastore.get(self.workspace, datastore_name)
        self.path = path_on_datasore
        self.name = name

        datapath = DataPath(self.datastore, path_on_datasore,name)
        compute_binding = DataPathComputeBinding(mode="mount")

        self.data = datapath.create_data_reference(data_reference_name = name, 
                                                       datapath_compute_binding=compute_binding)


    def __get_workspace(self, e):
        interactive_auth = InteractiveLoginAuthentication(tenant_id=e.TENANT_ID)
        workspace = Workspace.get(
            name=e.WORKSPACE_NAME,
            subscription_id=e.SUBSCRIPTION_ID,
            resource_group=e.RESOURCE_GROUP,
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



@dataclass(frozen=True)
class FileInputSchema:
    name: str
    datastore_name: str
    path_on_datastore: str
    data_reference_name: str
    files: List[str] | Dict[str, str]


@dataclass(frozen=True)
class PathInputSchema:
    name: str
    datastore_name: str
    path_on_datastore: str
    data_reference_name: str
