"""
Integration tests for configuration file loading
"""

import pytest
import tempfile
import json
import yaml

from pathlib import Path
from unittest.mock import Mock, patch

from flow_ctrl.src.cli.interface import FlowCLI
from flow_ctrl.src.config.settings import FlowConfig, DEFAULT_CONFIG
from flow_ctrl.tst.fixtures.test_config_files import (
    create_test_json_config,
    create_test_yaml_config,
    create_test_partial_config,
    create_invalid_json_config,
)


class TestConfigLoading:
    """Integration tests for configuration file loading"""

    def test_load_json_config_success(self, temp_dir):
        """Test successful loading of JSON configuration"""
        config_file = create_test_json_config(temp_dir)

        cli = FlowCLI()
        loaded_config = cli.load_config_from_file(str(config_file))

        assert loaded_config is not None
        assert loaded_config.project_dir == "/tmp/test_project"
        assert loaded_config.log_dir == "test_logs"
        assert loaded_config.log_file == "test.log"
        assert loaded_config.silence is True
        assert loaded_config.debug is True

    def test_load_yaml_config_success(self, temp_dir):
        """Test successful loading of YAML configuration"""
        config_file = create_test_yaml_config(temp_dir)

        cli = FlowCLI()
        loaded_config = cli.load_config_from_file(str(config_file))

        assert loaded_config is not None
        assert loaded_config.project_dir == "/tmp/yaml_test_project"
        assert loaded_config.log_dir == "yaml_logs"
        assert loaded_config.log_file == "yaml_test.log"
        assert loaded_config.silence is True
        assert loaded_config.debug is True

    def test_load_partial_config(self, temp_dir):
        """Test loading partial configuration with defaults"""
        config_file = create_test_partial_config(temp_dir)

        cli = FlowCLI()
        loaded_config = cli.load_config_from_file(str(config_file))

        assert loaded_config is not None
        assert loaded_config.project_dir == "/tmp/partial_project"
        assert loaded_config.log_file == "partial.log"
        assert loaded_config.debug is True
        # Should use defaults for missing fields
        assert loaded_config.log_dir == DEFAULT_CONFIG.log_dir
        assert loaded_config.silence == DEFAULT_CONFIG.silence

    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file"""
        cli = FlowCLI()
        loaded_config = cli.load_config_from_file("/nonexistent/config.json")

        assert loaded_config is None

    def test_load_invalid_json_config(self, temp_dir):
        """Test loading invalid JSON configuration"""
        config_file = create_invalid_json_config(temp_dir)

        cli = FlowCLI()
        loaded_config = cli.load_config_from_file(str(config_file))

        assert loaded_config is None

    def test_cli_with_config_file(self, temp_dir):
        """Test CLI with --config-file argument"""
        config_file = create_test_json_config(temp_dir)

        test_args = [
            "flow-ctrl",
            "--config-file",
            str(config_file),
            "--start",
            "--sketch-file",
            "test.json",
        ]

        with patch("sys.argv", test_args):
            with patch("flow_ctrl.src.cli.interface.FlowEngine") as mock_engine_class:
                mock_engine = Mock()
                mock_engine.load_procedure.return_value = True
                mock_engine.start_procedure.return_value = Mock(exit_code=0)
                mock_engine_class.return_value = mock_engine

                cli = FlowCLI()
                # This should not raise an exception
                cli.parse_arguments()

    def test_config_priority(self, temp_dir):
        """Test that CLI arguments override config file settings"""
        config_file = create_test_json_config(temp_dir)

        cli = FlowCLI()
        # Load config from file first
        file_config = cli.load_config_from_file(str(config_file))
        assert file_config is not None
        assert file_config.silence is True

        # Simulate CLI argument override
        cli.config = file_config
        # CLI argument should override config file
        cli.config.silence = False

        assert cli.config.silence is False
        assert cli.config.project_dir == "/tmp/test_project"  # Other settings preserved

    def test_flowconfig_from_file_classmethod(self, temp_dir):
        """Test FlowConfig.from_file class method"""
        config_file = create_test_json_config(temp_dir)

        config = FlowConfig.from_file(str(config_file))

        assert config is not None
        assert config.project_dir == "/tmp/test_project"
        assert config.log_file == "test.log"
        assert isinstance(config, FlowConfig)

    def test_flowconfig_from_file_with_base(self, temp_dir):
        """Test FlowConfig.from_file with base configuration"""
        config_file = create_test_partial_config(temp_dir)

        base_config = FlowConfig(
            project_dir="/base/project",
            log_dir="base_logs",
            log_file="base.log",
            silence=False,
            debug=False,
        )

        config = FlowConfig.from_file(str(config_file), base_config)

        assert config.project_dir == "/tmp/partial_project"  # From file
        assert config.log_file == "partial.log"  # From file
        assert config.log_dir == "base_logs"  # From base (not in file)
        assert config.debug is True  # From file
        assert config.silence is False  # From base (not overridden in file)
