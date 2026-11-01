"""Root-level pytest configuration and fixtures for {{PROJECT_NAME}} QA automation."""

import logging
import os
from pathlib import Path

import pytest
from features.utils.config_manager import ConfigManager
from features.utils.auth_setup import AuthSetup


def pytest_configure(config):
    """Configure pytest and initialize framework components."""
    # Enable strict marker checking
    config.option.strict_markers = True

    # Initialize ConfigManager (loads config.yml, env vars, AWS Secrets Manager)
    ConfigManager.initialize()
    logger = logging.getLogger(__name__)
    logger.info(f"Environment: {ConfigManager.get('environment')}")
    logger.info(f"Browser: {ConfigManager.get('browser')}")


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context arguments."""
    return {
        "ignore_https_errors": True,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture(scope="function", autouse=True)
def test_logger():
    """Provide a logger for tests."""
    logger = logging.getLogger(__name__)
    yield logger


@pytest.fixture(scope="session")
def auth_setup():
    """Initialize authentication setup for the test session."""
    return AuthSetup()
