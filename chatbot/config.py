import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Redis Configuration
    REDIS_ENDPOINT: str = Field(..., env="REDIS_ENDPOINT")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_SSL: bool = Field(default=True, env="REDIS_SSL")
    REDIS_SECRET_NAME: Optional[str] = Field(default=None, env="REDIS_SECRET_NAME")
    
    # AWS Bedrock Configuration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN: Optional[str] = Field(default="", env="AWS_SESSION_TOKEN")
    
    # Bedrock Model Configuration
    BEDROCK_MODEL_ID: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0", 
        env="BEDROCK_MODEL_ID"
    )
    BEDROCK_REGION: str = Field(default="us-east-1", env="BEDROCK_REGION")
    
    # Application Configuration
    APP_TITLE: str = Field(default="AI Chatbot with Bedrock & Redis", env="APP_TITLE")
    MAX_TOKENS: int = Field(default=4000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")
    TOP_P: float = Field(default=0.9, env="TOP_P")
    SESSION_TIMEOUT: int = Field(default=3600, env="SESSION_TIMEOUT")  # 1 hour
    MAX_HISTORY_LENGTH: int = Field(default=50, env="MAX_HISTORY_LENGTH")
    
    # Available Bedrock Claude Models
    AVAILABLE_MODELS: List[str] = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",  # Latest Claude 3.5 Sonnet
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-opus-20240229-v1:0"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()