from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Env:
    load_dotenv()
    local_data_path: Optional[str] = os.environ.get("LOCAL_DATA_PATH", ".")
    workspace_name: Optional[str] = os.environ.get("WORKSPACE_NAME")
    resource_group: Optional[str] = os.environ.get("RESOURCE_GROUP")
    subscription_id: Optional[str] = os.environ.get("SUBSCRIPTION_ID")
    build_id: Optional[str] = os.environ.get("BUILD_BUILDID")
    environment_name: Optional[str] = os.environ.get("ENVIRONMENT_NAME")
    environment_file: Optional[str] = os.environ.get("ENVIRONMENT_FILE")
    tenant_id: Optional[str] = os.environ.get("TENANT_ID")


def get_env():
    return Env()

