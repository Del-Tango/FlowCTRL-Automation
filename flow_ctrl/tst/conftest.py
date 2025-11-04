"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock

from flow_ctrl.src.config.settings import FlowConfig, DEFAULT_CONFIG
from tests.fixtures.test_config import create_test_config, create_mock_config, cleanup_test_config


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration"""
    config = create_test_config(temp_dir)
    yield config
    # Cleanup after test
    cleanup_test_config(config)


@pytest.fixture
def mock_config():
    """Create mock configuration for unit testing"""
    return create_mock_config()


@pytest.fixture
def minimal_config():
    """Create minimal test configuration"""
    config = TestConfigFactory.create_minimal_config()
    yield config
    cleanup_test_config(config)


@pytest.fixture
def debug_config():
    """Create debug test configuration"""
    config = TestConfigFactory.create_debug_config()
    yield config
    cleanup_test_config(config)


@pytest.fixture
def mock_shell_executor():
    """Mock shell executor for testing"""
    mock_executor = Mock()
    mock_executor.execute.return_value = Mock(stdout="test output", stderr="", exit_code=0)
    mock_executor.execute_with_timeout.return_value = Mock(stdout="test output", stderr="", exit_code=0)
    mock_executor.check_command_exists.return_value = True
    mock_executor.execute_detached.return_value = 0
    return mock_executor


@pytest.fixture
def simple_sketch_file(temp_dir):
    """Create a simple sketch file for testing"""
    sketch_data = {
        "name": "Test Procedure",
        "stage_1": [
            {
                "name": "test_action",
                "cmd": "echo 'Hello World'",
                "time": "5s",
                "timeout": "10s"
            }
        ]
    }

    sketch_file = temp_dir / "simple_sketch.json"
    sketch_file.write_text(json.dumps(sketch_data))
    return sketch_file


@pytest.fixture
def multi_stage_sketch_file(temp_dir):
    """Create a multi-stage sketch file for testing"""
    sketch_data = {
        "name": "Multi-Stage Test",
        "setup_stage": [
            {
                "name": "create_test_dir",
                "cmd": "mkdir -p /tmp/test_dir",
                "time": "5s"
            }
        ],
        "main_stage": [
            {
                "name": "list_files",
                "cmd": "ls -la /tmp/test_dir",
                "time": "5s"
            }
        ],
        "cleanup_stage": [
            {
                "name": "remove_test_dir",
                "cmd": "rm -rf /tmp/test_dir",
                "time": "5s"
            }
        ]
    }

    sketch_file = temp_dir / "multi_stage_sketch.json"
    sketch_file.write_text(json.dumps(sketch_data))
    return sketch_file


@pytest.fixture
def invalid_sketch_file(temp_dir):
    """Create an invalid sketch file for testing"""
    sketch_data = {
        "stage_1": [
            {
                "name": "invalid_action",
                # Missing required 'cmd' field
                "time": "invalid_time"
            }
        ]
    }

    sketch_file = temp_dir / "invalid_sketch.json"
    sketch_file.write_text(json.dumps(sketch_data))
    return sketch_file


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Auto-cleanup temporary files after each test"""
    # Setup
    yield
    # Teardown - any additional cleanup can go here

# CODE DUMP

#   """
#   Pytest configuration and shared fixtures
#   """

#   import pytest
#   import tempfile
#   import json
#   from pathlib import Path
#   from unittest.mock import Mock

#   from flow_ctrl.src.config.settings import FlowConfig, DEFAULT_CONFIG


#   @pytest.fixture
#   def temp_dir():
#       """Create temporary directory for test files"""
#       with tempfile.TemporaryDirectory() as tmp_dir:
#           yield Path(tmp_dir)


#   @pytest.fixture
#   def test_config(temp_dir):
#       """Create test configuration"""
#       return FlowConfig(
#           project_dir=str(temp_dir),
#           log_dir="logs",
#           conf_dir="conf",
#           state_file=str(temp_dir / ".flow-ctrl.state.tmp"),
#           report_file=str(temp_dir / ".flow-ctrl.report.tmp"),
#           log_file="test-flow-ctrl.log",
#           log_name="TestFlowCTRL",
#           silence=True,
#           debug=True
#       )


#   @pytest.fixture
#   def mock_shell_executor():
#       """Mock shell executor for testing"""
#       mock_executor = Mock()
#       mock_executor.execute.return_value = Mock(stdout="test output", stderr="", exit_code=0)
#       mock_executor.execute_with_timeout.return_value = Mock(stdout="test output", stderr="", exit_code=0)
#       mock_executor.check_command_exists.return_value = True
#       return mock_executor
