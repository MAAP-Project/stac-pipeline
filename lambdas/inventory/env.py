from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class InventoryEnv(BaseSettings):
    
    model_config = SettingsConfigDict(env_prefix='INVENTORY_', env_file='.env')
        
    file_location : str = Field(description="S3 path to a CSV inventory file")
    
    file_key: str = Field(description="column name in the CSV file to use as a task list")
    
