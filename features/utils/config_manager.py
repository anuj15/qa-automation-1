"""Configuration manager for test settings and secrets."""

from functools import cache
import json
import logging
import os
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError
import yaml


def is_ci() -> bool:
    """Return True if running inside GitHub Actions."""
    return os.getenv("GITHUB_ACTIONS", "false").lower() == "true"


class ConfigManager:
    """Centralized configuration loader for test settings, credentials, and AWS Secrets Manager integration."""

    _instance: Optional["ConfigManager"] = None

    def __init__(self) -> None:
        """Load config.yml from repo root."""
        self.logger = logging.getLogger(__name__)

        # In CI GITHUB_WORKSPACE points to the repo root; locally walk up 2 levels from this file
        self.root_dir = os.getenv("GITHUB_WORKSPACE") or str(Path(__file__).resolve().parents[2])
        config_path = Path(self.root_dir) / "config.yml"

        with open(config_path, encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

        # Select active environment from env var or config
        self.env: str = os.environ.get("environment") or self.data["environment"]
        self.env_config: dict = self.data[self.env]

        self._load_aws_secrets_into_env()

    def _load_aws_secrets_into_env(self) -> None:
        """Fetch secrets from AWS Secrets Manager and inject into os.environ."""
        try:
            aws_region = self.get("aws_region")
            if is_ci():
                client = boto3.client("secretsmanager", region_name=aws_region)
            else:
                client = boto3.Session(profile_name="automation", region_name=aws_region).client("secretsmanager")

            # Iterate over all secrets defined in config.yml
            for secret_name in self.data.get("secrets", {}).values():
                try:
                    response = client.get_secret_value(SecretId=secret_name)
                    secret_value = response.get("SecretString")
                    if secret_value:
                        os.environ.setdefault(secret_name, secret_value)
                except ClientError:
                    self.logger.warning(f"Failed to fetch secret: {secret_name}")
        except (ClientError, BotoCoreError) as exc:
            if is_ci():
                self.logger.warning("AWS Secrets Manager call failed in CI; continuing with existing environment variables.")
                return
            self.logger.warning(f"AWS Secrets Manager call failed: {exc}")

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a configuration value with priority:
        1. Environment variable
        2. Environment-specific config (config.yml[env][key])
        3. Global config (config.yml[key])
        """
        # Check environment variable first
        if key in os.environ:
            return os.environ[key]

        # Check environment-specific config
        if key in self.env_config:
            return self.env_config[key]

        # Check global config
        return self.data.get(key)

    def get_credential(self, field: str, user_type: str = "default") -> Optional[str]:
        """
        Retrieve a credential from environment following naming convention:
        {{PROJECT_NAME}}_{ENV}_{USER_TYPE}_{FIELD}
        """
        project_name = self.data.get("project_name", "").upper().replace(" ", "_")
        env_upper = self.env.upper()
        user_upper = user_type.upper()
        key = f"{project_name}_{env_upper}_{user_upper}_{field.upper()}"
        return os.environ.get(key)

    @classmethod
    def initialize(cls) -> "ConfigManager":
        """Initialize and cache the ConfigManager singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        """Get the cached ConfigManager instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Global accessor function
@cache
def get_config() -> ConfigManager:
    """Return the singleton ConfigManager instance."""
    return ConfigManager.get_instance()
