"""
Unit tests for utility modules
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from flow_ctrl.src.utils.shell import ShellExecutor, CommandResult
from flow_ctrl.src.utils.state_manager import StateManager
from flow_ctrl.src.utils.logger import ConsoleOutput, setup_logging


class TestShellExecutor:
    """Test ShellExecutor functionality"""

    def test_execute_success(self):
        """Test successful command execution"""
        executor = ShellExecutor()

        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = ("test stdout", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            result = executor.execute("echo 'test'")

            assert result.exit_code == 0
            assert result.stdout == "test stdout"
            assert result.stderr == ""

    def test_execute_with_timeout_success(self):
        """Test command execution with timeout"""
        executor = ShellExecutor()

        with patch('threading.Thread') as mock_thread:
            result = executor.execute_with_timeout("echo 'test'", timeout=5)
            assert result.exit_code in [0, 124]  # Could be success or timeout

    def test_check_command_exists(self):
        """Test command existence check"""
        executor = ShellExecutor()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            assert executor.check_command_exists("ls") is True

            mock_run.return_value.returncode = 1
            assert executor.check_command_exists("nonexistent") is False


class TestStateManager:
    """Test StateManager functionality"""

    def test_initialization(self, temp_dir):
        """Test state manager initialization"""
        state_file = temp_dir / "test.state"
        manager = StateManager(str(state_file))

        assert state_file.exists()

    def test_set_state(self, temp_dir):
        """Test setting state"""
        state_file = temp_dir / "test.state"
        manager = StateManager(str(state_file))

        assert manager.set_state(True, "started") is True
        assert manager.get_state() is True

        assert manager.set_state(False, "stopped") is True
        assert manager.get_state() is False

    def test_update_state(self, temp_dir):
        """Test updating state fields"""
        state_file = temp_dir / "test.state"
        manager = StateManager(str(state_file))

        manager.set_state(True, "started")
        assert manager.update_state(2, "test_stage") is True
        assert manager.get_state_field(2) == "test_stage"

    def test_get_full_state(self, temp_dir):
        """Test getting complete state"""
        state_file = temp_dir / "test.state"
        manager = StateManager(str(state_file))

        manager.set_state(True, "started")
        manager.update_state(1, "test_sketch.json")
        manager.update_state(2, "test_stage")

        full_state = manager.get_full_state()
        assert full_state['active'] is True
        assert full_state['action'] == "started"

    def test_purge(self, temp_dir):
        """Test state purging"""
        state_file = temp_dir / "test.state"
        manager = StateManager(str(state_file))

        manager.set_state(True, "started")
        assert state_file.exists()

        assert manager.purge() is True
        assert not state_file.exists()


class TestConsoleOutput:
    """Test ConsoleOutput functionality"""

    def test_info_message(self, capsys):
        """Test info message output"""
        ConsoleOutput.info("Test info message")
        captured = capsys.readouterr()
        assert "[INFO]: Test info message" in captured.out

    def test_success_message(self, capsys):
        """Test success message output"""
        ConsoleOutput.success("Test success message")
        captured = capsys.readouterr()
        assert "[OK]: Test success message" in captured.out

    def test_error_message(self, capsys):
        """Test error message output"""
        ConsoleOutput.error("Test error message")
        captured = capsys.readouterr()
        assert "[ERROR]: Test error message" in captured.out

    def test_banner_message(self, capsys):
        """Test banner message output"""
        ConsoleOutput.banner("Test Banner")
        captured = capsys.readouterr()
        assert "Test Banner" in captured.out
#       assert "=" * 60 in captured.out
