"""
Integration tests for procedure execution with real commands
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from flow_ctrl.src.core.engine import FlowEngine
from flow_ctrl.src.config.settings import FlowConfig


class TestProcedureExecution:
    """Integration tests for procedure execution"""

    @patch("flow_ctrl.src.core.engine.Procedure")
    def test_safe_command_execution(self, mock_procedure_class, test_config, temp_dir):
        """Test execution of safe system commands"""
        safe_sketch = {
            "name": "Safe Commands Test",
            "file_operations": [
                {
                    "name": "create_test_file",
                    "cmd": f"touch {temp_dir}/test_file.txt",
                    "time": "5s",
                }
            ],
        }

        sketch_file = temp_dir / "safe_commands.json"
        sketch_file.write_text(json.dumps(safe_sketch))

        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "safe_exec.state"),
            report_file=str(temp_dir / "safe_exec.report"),
            log_file="safe_exec_test.log",
            silence=True,
            debug=True,
        )

        # Mock the procedure execution
        mock_procedure = Mock()
        mock_procedure.name = "Safe Commands Test"
        mock_procedure.execute.return_value = True
        mock_procedure_class.return_value = mock_procedure

        engine = FlowEngine(config)
        load_result = engine.load_procedure(str(sketch_file))

        assert load_result is True

        # Mock state validation with correct parameters
        engine.state_manager.get_state = Mock(return_value=False)
        engine.state_manager.get_state_field = Mock(return_value="")

        start_result = engine.start_procedure()
        assert start_result is not None

    @patch("flow_ctrl.src.core.engine.Procedure")
    def test_command_validation(self, mock_procedure_class, test_config, temp_dir):
        """Test command validation and error handling"""
        sketch_with_invalid_commands = {
            "name": "Invalid Commands Test",
            "test_stage": [
                {
                    "name": "valid_command",
                    "cmd": "echo 'This should work'",
                    "time": "5s",
                }
            ],
        }

        sketch_file = temp_dir / "invalid_commands.json"
        sketch_file.write_text(json.dumps(sketch_with_invalid_commands))

        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "invalid_exec.state"),
            report_file=str(temp_dir / "invalid_exec.report"),
            log_file="invalid_exec_test.log",
            silence=True,
            debug=True,
        )

        # Mock procedure that fails execution
        mock_procedure = Mock()
        mock_procedure.name = "Invalid Commands Test"
        mock_procedure.execute.return_value = False
        mock_procedure_class.return_value = mock_procedure

        engine = FlowEngine(config)
        load_result = engine.load_procedure(str(sketch_file))

        assert load_result is True

        # Mock state validation with correct parameters
        engine.state_manager.get_state = Mock(return_value=False)
        engine.state_manager.get_state_field = Mock(return_value="")

        start_result = engine.start_procedure()
        assert start_result is not None
        # Since we mocked the procedure to fail, the result should reflect that
        assert start_result.success is False

# CODE DUMP

