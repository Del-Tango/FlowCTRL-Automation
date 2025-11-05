"""
Test configuration files for configuration loading tests
"""

import tempfile
import json
import yaml

from pathlib import Path

# JSON configuration for testing
JSON_CONFIG = {
    "project_dir": "/tmp/test_project",
    "log_dir": "test_logs",
    "conf_dir": "test_conf",
    "state_file": ".test.state",
    "report_file": ".test.report",
    "log_file": "test.log",
    "log_name": "TestFlowCTRL",
    "silence": True,
    "debug": True,
    "log_format": "%(asctime)s - TEST - %(levelname)s - %(message)s",
    "timestamp_format": "%Y-%m-%d %H:%M:%S",
}

# YAML configuration for testing
YAML_CONFIG = """
project_dir: /tmp/yaml_test_project
log_dir: yaml_logs
conf_dir: yaml_conf
state_file: .yaml_test.state
report_file: .yaml_test.report
log_file: yaml_test.log
log_name: YamlTestFlowCTRL
silence: true
debug: true
log_format: "%(asctime)s - YAML - %(levelname)s - %(message)s"
timestamp_format: "%Y-%m-%d %H:%M:%S"
"""

# Partial configuration (missing some fields)
PARTIAL_CONFIG = {
    "project_dir": "/tmp/partial_project",
    "log_file": "partial.log",
    "debug": True,
}


def create_test_json_config(temp_dir: Path) -> Path:
    """Create a test JSON configuration file"""
    config_file = temp_dir / "test_config.json"
    config_file.write_text(json.dumps(JSON_CONFIG, indent=2))
    return config_file


def create_test_yaml_config(temp_dir: Path) -> Path:
    """Create a test YAML configuration file"""
    config_file = temp_dir / "test_config.yaml"
    config_file.write_text(YAML_CONFIG)
    return config_file


def create_test_partial_config(temp_dir: Path) -> Path:
    """Create a test partial configuration file"""
    config_file = temp_dir / "partial_config.json"
    config_file.write_text(json.dumps(PARTIAL_CONFIG, indent=2))
    return config_file


def create_invalid_json_config(temp_dir: Path) -> Path:
    """Create an invalid JSON configuration file"""
    config_file = temp_dir / "invalid_config.json"
    config_file.write_text("{ invalid json }")
    return config_file
