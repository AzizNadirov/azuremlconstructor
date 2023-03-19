from azureml.core import Workspace, Datastore
from azureml.data.datapath import DataPath, DataPathComputeBinding
from azureml.core.authentication import InteractiveLoginAuthentication

from amlctor.apply.env import get_env


env = get_env()




class FileInput:
    def __init__(self, name: str, 
                filename: list,
                datastore_name: str, 
                path_on_datasore: str, 
                data_reference_name: str = ''):
        
        if data_reference_name == '':
            data_reference_name = name
        e = env
        compute_binding = DataPathComputeBinding(mode="mount")
        self.data_reference_name = data_reference_name

        self.workspace = self.get_workspace(e)
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


    def get_workspace(self, e):
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
    def __init__(self, name: str, datastore_name: str, path_on_datasore: str):
        e = env
        self.workspace = self.get_workspace(e)
        self.datastore = Datastore.get(self.workspace, datastore_name)
        self.path = path_on_datasore
        self.name = name

    def get_workspace(self, e):
        interactive_auth = InteractiveLoginAuthentication(tenant_id=e.tenant_id)
        workspace = Workspace.get(
            name=e.workspace_name,
            subscription_id=e.subscription_id,
            resource_group=e.resource_group,
            auth=interactive_auth
        )
        return workspace
    

    def upload(self, filenames: list, overwrite=True, show_progress=True):
        self.data_store.upload_files(files=filenames,
                                     target_path=self.path,
                                     overwrite=overwrite,
                                     show_progress=show_progress)
