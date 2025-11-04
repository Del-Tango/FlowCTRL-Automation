"""
Unit tests for Validator
"""

import pytest
import tempfile
import json
from pathlib import Path

from flow_ctrl.src.core.validator import Validator
from flow_ctrl.tst.fixtures.sample_sketches import SIMPLE_SKETCH, INVALID_SKETCH


class TestValidator:
    """Test Validator functionality"""

    def setup_method(self):
        self.validator = Validator()

    def test_validate_instruction_dict(self):
        """Test dictionary instruction validation"""
        assert self.validator.validate_instruction({"key": "value"}) is True
        assert self.validator.validate_instruction({}) is False

    def test_validate_instruction_list(self, temp_dir):
        """Test list instruction validation"""
        # Create temporary files for testing
        file1 = temp_dir / "test1.json"
        file2 = temp_dir / "test2.json"
        file1.write_text('{"test": "data"}')
        file2.write_text('{"test": "data"}')

        valid_list = [str(file1), str(file2)]
        invalid_list = [str(file1), "/nonexistent/path.json"]

        assert self.validator.validate_instruction(valid_list) is True
        assert self.validator.validate_instruction(invalid_list) is False

    def test_validate_state_transitions(self):
        """Test state transition validation"""
        # Valid transitions
        assert self.validator.validate_state(False, "", "start") is True
        assert self.validator.validate_state(True, "started", "stop") is True
        assert self.validator.validate_state(True, "paused", "resume") is True

        # Invalid transitions
        assert self.validator.validate_state(True, "started", "start") is False
        assert self.validator.validate_state(False, "", "stop") is False

    def test_validate_action_config(self):
        """Test action configuration validation"""
        valid_action = {
            "name": "test_action",
            "cmd": "echo 'test'",
            "time": "5s",
            "timeout": "10s"
        }

        invalid_action_missing_name = {
            "cmd": "echo 'test'"
        }

        invalid_action_missing_cmd = {
            "name": "test_action"
        }

        assert self.validator.validate_action_config(valid_action) is True
        assert self.validator.validate_action_config(invalid_action_missing_name) is False
        assert self.validator.validate_action_config(invalid_action_missing_cmd) is False

    def test_validate_time_format(self):
        """Test time format validation"""
        assert self.validator._validate_time_format("5s") is True
        assert self.validator._validate_time_format("10m") is True
        assert self.validator._validate_time_format("1h") is True
        assert self.validator._validate_time_format("2d") is True
        assert self.validator._validate_time_format("invalid") is False
        assert self.validator._validate_time_format("") is True

    def test_validate_sketch_file(self, temp_dir):
        """Test sketch file validation"""
        # Valid sketch file
        valid_sketch = temp_dir / "valid_sketch.json"
        valid_sketch.write_text(json.dumps(SIMPLE_SKETCH))

        # Invalid sketch file
        invalid_sketch = temp_dir / "invalid_sketch.json"
        invalid_sketch.write_text(json.dumps(INVALID_SKETCH))

        # Non-existent file
        nonexistent_file = temp_dir / "nonexistent.json"

        # Non-JSON file
        non_json_file = temp_dir / "non_json.txt"
        non_json_file.write_text("not json")

        assert self.validator.validate_sketch_file(str(valid_sketch)) is True
        assert self.validator.validate_sketch_file(str(invalid_sketch)) is False
        assert self.validator.validate_sketch_file(str(nonexistent_file)) is False
        assert self.validator.validate_sketch_file(str(non_json_file)) is False
