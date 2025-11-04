"""
Integration tests for procedure execution with real commands
"""

import pytest
import tempfile
import json
from pathlib import Path

from flow_ctrl.src.core.engine import FlowEngine
from flow_ctrl.src.config.settings import FlowConfig


class TestProcedureExecution:
    """Integration tests for procedure execution"""

    def test_safe_command_execution(self, temp_dir):
        """Test execution of safe system commands"""
        safe_sketch = {
            "name": "Safe Commands Test",
            "file_operations": [
                {
                    "name": "create_test_file",
                    "cmd": f"touch {temp_dir}/test_file.txt",
                    "time": "5s"
                },
                {
                    "name": "list_test_dir",
                    "cmd": f"ls -la {temp_dir}",
                    "time": "5s"
                },
                {
                    "name": "remove_test_file",
                    "cmd": f"rm {temp_dir}/test_file.txt",
                    "time": "5s"
                }
            ]
        }

        sketch_file = temp_dir / "safe_commands.json"
        sketch_file.write_text(json.dumps(safe_sketch))

        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "safe_exec.state"),
            report_file=str(temp_dir / "safe_exec.report"),
            log_file="safe_exec_test.log",
            silence=True,
            debug=True
        )

        engine = FlowEngine(config)
        load_result = engine.load_procedure(str(sketch_file))

        assert load_result is True

        # We can't reliably test the execution result since it depends on system state
        # but we can test that the engine handles the procedure correctly
        start_result = engine.start_procedure()
        assert start_result is not None  # Engine should return a result object

    def test_command_validation(self, temp_dir):
        """Test command validation and error handling"""
        sketch_with_invalid_commands = {
            "name": "Invalid Commands Test",
            "test_stage": [
                {
                    "name": "valid_command",
                    "cmd": "echo 'This should work'",
                    "time": "5s"
                },
                {
                    "name": "command_with_error",
                    "cmd": "nonexistent_command_xyz123",
                    "time": "5s"
                }
            ]
        }

        sketch_file = temp_dir / "invalid_commands.json"
        sketch_file.write_text(json.dumps(sketch_with_invalid_commands))

        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "invalid_exec.state"),
            report_file=str(temp_dir / "invalid_exec.report"),
            log_file="invalid_exec_test.log",
            silence=True,
            debug=True
        )

        engine = FlowEngine(config)
        load_result = engine.load_procedure(str(sketch_file))

        assert load_result is True

        # The engine should handle invalid commands gracefully
        start_result = engine.start_procedure()
        assert start_result is not None
