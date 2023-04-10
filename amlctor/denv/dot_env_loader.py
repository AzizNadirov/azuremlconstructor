from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv, dotenv_values


@dataclass(frozen=True)
class Env:
    workspace_name: Optional[str] = os.environ.get("WORKSPACE_NAME")
    resource_group: Optional[str] = os.environ.get("RESOURCE_GROUP")
    subscription_id: Optional[str] = os.environ.get("SUBSCRIPTION_ID")
    build_id: Optional[str] = os.environ.get("BUILD_ID")
    environment_name: Optional[str] = os.environ.get("ENVIRONMENT_NAME")
    environment_file: Optional[str] = os.environ.get("ENVIRONMENT_FILE")
    tenant_id: Optional[str] = os.environ.get("TENANT_ID")


def get_env(pipe_path: str):
    if not load_dotenv(pipe_path): raise ValueError('Upps env...')
    d = dotenv_values(pipe_path)
    d = {k.lower(): v for k, v in d.items()}
    e = Env(**d)
    return e

