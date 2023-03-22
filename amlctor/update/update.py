from pathlib import Path
from typing import Union

from amlctor.utils import is_pipe, get_settingspy_module



class UpdateHandler:
    def __init__(self, path: Path, is_step: Union[str, bool]) -> None:
        self.path = path
        self.is_step = is_step


    def validate(self):
        pass



    def start(self):
        pass