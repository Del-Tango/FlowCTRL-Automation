"""
Unit tests for Action class
"""

import pytest
from unittest.mock import Mock, patch

from flow_ctrl.src.core.action import Action
from flow_ctrl.src.config.settings import FlowConfig


class TestAction:
    """Test Action functionality"""

    def test_action_initialization(self, test_config):
        """Test action initialization"""
        action_data = {
            "name": "test_action",
            "cmd": "echo 'test'",
            "setup-cmd": "echo 'setup'",
            "teardown-cmd": "echo 'teardown'",
            "on-ok-cmd": "echo 'on_ok'",
            "on-nok-cmd": "echo 'on_nok'",
            "time": "5s",
            "timeout": "10s",
            "fatal-nok": True,
        }

        action = Action(action_data, test_config)

        assert action.name == "test_action"
        assert action.command == "echo 'test'"
        assert action.setup_command == "echo 'setup'"
        assert action.teardown_command == "echo 'teardown'"
        assert action.fatal_nok is True
        assert action.timeout == 10  # 10s in seconds
        assert action.estimated_time == 5  # 5s in seconds

    def test_parse_time(self, test_config):
        """Test time parsing"""
        action_data = {"name": "test", "cmd": "echo 'test'"}
        action = Action(action_data, test_config)

        assert action._parse_time("5s") == 5
        assert action._parse_time("10m") == 600
        assert action._parse_time("1h") == 3600
        assert action._parse_time("2d") == 172800
        assert action._parse_time("invalid") is None
        assert action._parse_time("") is None

    def test_validate_action(self, test_config):
        """Test action validation"""
        valid_action_data = {"name": "test", "cmd": "echo 'test'"}
        invalid_action_data = {"name": "test"}  # Missing cmd

        valid_action = Action(valid_action_data, test_config)
        invalid_action = Action(invalid_action_data, test_config)

        assert valid_action.validate() is True
        assert invalid_action.validate() is False

    @patch("flow_ctrl.src.core.action.ShellExecutor")
    def test_execute_success(self, mock_shell_class, test_config):
        """Test successful action execution"""
        mock_shell = Mock()
        mock_shell_class.return_value = mock_shell
        mock_shell.execute.return_value = Mock(exit_code=0, stdout="success", stderr="")

        action_data = {
            "name": "test_action",
            "cmd": "echo 'test'",
            "setup-cmd": "echo 'setup'",
            "on-ok-cmd": "echo 'on_ok'",
            "teardown-cmd": "echo 'teardown'",
        }

        action = Action(action_data, test_config)
        result = action.execute()

        assert result is True
        assert mock_shell.execute.call_count == 4  # setup, main, on-ok, teardown

    @patch("flow_ctrl.src.core.action.ShellExecutor")
    def test_execute_failure(self, mock_shell_class, test_config):
        """Test failed action execution"""
        mock_shell = Mock()
        mock_shell_class.return_value = mock_shell
        mock_shell.execute.return_value = Mock(exit_code=1, stdout="", stderr="error")

        action_data = {
            "name": "test_action",
            "cmd": "echo 'test'",
            "on-nok-cmd": "echo 'on_nok'",
        }

        action = Action(action_data, test_config)
        result = action.execute()

        assert result is False
        # Should execute main command and on-nok command
        assert mock_shell.execute.call_count == 2
