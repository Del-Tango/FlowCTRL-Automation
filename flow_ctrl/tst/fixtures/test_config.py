"""
Test configuration fixtures and utilities
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from flow_ctrl.src.config.settings import FlowConfig, DEFAULT_CONFIG


def create_test_config(temp_dir: Path = None) -> FlowConfig:
    """
    Create a test configuration with temporary paths

    Args:
        temp_dir: Temporary directory for test files. If None, creates one.

    Returns:
        FlowConfig: Test configuration instance
    """
    if temp_dir is None:
        temp_dir = Path(tempfile.mkdtemp())

    return FlowConfig(
        project_dir=str(temp_dir),
        log_dir="test_logs",
        conf_dir="test_conf",
        state_file=str(temp_dir / ".flow-ctrl.test.state"),
        report_file=str(temp_dir / ".flow-ctrl.test.report"),
        log_file="test-flow-ctrl.log",
        log_name="TestFlowCTRL",
        silence=True,  # Suppress output during tests
        debug=True,  # Enable debug logging for tests
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        timestamp_format="%H:%M:%S",
    )


def create_mock_config(**overrides) -> Mock:
    """
    Create a mock configuration for unit testing

    Args:
        **overrides: Configuration overrides

    Returns:
        Mock: Mock configuration object
    """
    mock_config = Mock(spec=FlowConfig)

    # Default values
    default_values = {
        "project_dir": "/tmp/test_project",
        "log_dir": "logs",
        "conf_dir": "conf",
        "state_file": "/tmp/.flow-ctrl.test.state",
        "report_file": "/tmp/.flow-ctrl.test.report",
        "log_file": "test.log",
        "log_name": "TestFlowCTRL",
        "silence": True,
        "debug": True,
        "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "timestamp_format": "%H:%M:%S",
    }

    # Apply defaults and overrides
    for key, value in {**default_values, **overrides}.items():
        setattr(mock_config, key, value)

    return mock_config


class TestConfigFactory:
    """Factory for creating different types of test configurations"""

    @staticmethod
    def create_minimal_config() -> FlowConfig:
        """Create minimal configuration with only required fields"""
        temp_dir = Path(tempfile.mkdtemp())
        return FlowConfig(project_dir=str(temp_dir))

    @staticmethod
    def create_production_like_config() -> FlowConfig:
        """Create configuration that mimics production settings"""
        temp_dir = Path(tempfile.mkdtemp())
        return FlowConfig(
            project_dir=str(temp_dir),
            log_dir="logs",
            conf_dir="conf",
            state_file="/tmp/.flow-ctrl.prod.state",
            report_file="/tmp/.flow-ctrl.prod.report",
            log_file="flow-ctrl.log",
            log_name="FlowCTRL",
            silence=False,  # Production shows output
            debug=False,  # Production uses INFO level
            log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            timestamp_format="%Y-%m-%d %H:%M:%S",
        )

    @staticmethod
    def create_debug_config() -> FlowConfig:
        """Create configuration with debug settings enabled"""
        temp_dir = Path(tempfile.mkdtemp())
        return FlowConfig(
            project_dir=str(temp_dir),
            log_dir="debug_logs",
            conf_dir="debug_conf",
            state_file=str(temp_dir / ".flow-ctrl.debug.state"),
            report_file=str(temp_dir / ".flow-ctrl.debug.report"),
            log_file="debug-flow-ctrl.log",
            log_name="DebugFlowCTRL",
            silence=False,
            debug=True,  # Debug mode enabled
            log_format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            timestamp_format="%H:%M:%S",
        )


# Pre-configured test configurations for common use cases
MINIMAL_CONFIG = TestConfigFactory.create_minimal_config()
PRODUCTION_CONFIG = TestConfigFactory.create_production_like_config()
DEBUG_CONFIG = TestConfigFactory.create_debug_config()


def validate_test_config(config: FlowConfig) -> bool:
    """
    Validate that a test configuration has all required fields

    Args:
        config: Configuration to validate

    Returns:
        bool: True if configuration is valid
    """
    required_fields = [
        "project_dir",
        "log_dir",
        "conf_dir",
        "state_file",
        "report_file",
        "log_file",
        "log_name",
        "silence",
        "debug",
    ]

    for field in required_fields:
        if not hasattr(config, field):
            return False
        if getattr(config, field) is None:
            return False

    return True


def cleanup_test_config(config: FlowConfig):
    """
    Clean up files created by a test configuration

    Args:
        config: Configuration to clean up
    """
    import os
    from pathlib import Path

    # Clean up state and report files
    for file_path in [config.state_file, config.report_file]:
        path = Path(file_path)
        if path.exists():
            path.unlink()

    # Clean up log directory if it's in temp
    log_dir = Path(config.project_dir) / config.log_dir
    if log_dir.exists() and str(log_dir).startswith("/tmp"):
        import shutil

        shutil.rmtree(log_dir, ignore_errors=True)
