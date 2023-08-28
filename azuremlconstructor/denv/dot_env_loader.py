from dataclasses import dataclass
from pathlib import Path
import os
from typing import Optional

from dotenv import load_dotenv, dotenv_values


@dataclass
class Env:
    WORKSPACE_NAME: Optional[str] = os.environ.get("WORKSPACE_NAME")
    RESOURCE_GROUP: Optional[str] = os.environ.get("RESOURCE_GROUP")
    SUBSCRIPTION_ID: Optional[str] = os.environ.get("SUBSCRIPTION_ID")
    BUILD_ID: Optional[str] = os.environ.get("BUILD_ID")
    ENVIRONMENT_NAME: Optional[str] = os.environ.get("ENVIRONMENT_NAME")
    ENVIRONMENT_FILE: Optional[str] = os.environ.get("ENVIRONMENT_FILE")
    TENANT_ID: Optional[str] = os.environ.get("TENANT_ID")


def get_env(pipe_path: Path):
    if not load_dotenv(pipe_path): 
        raise ValueError('Upps env...')
    
    d = dotenv_values(pipe_path)
    e = Env(**d)
    return e

