"""
Unit tests for FlowEngine
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from flow_ctrl.src.core.engine import FlowEngine
from flow_ctrl.tst.fixtures.sample_sketches import SIMPLE_SKETCH


class TestFlowEngine:
    """Test FlowEngine functionality"""

    def test_engine_initialization(self, test_config):
        """Test engine initialization"""
        engine = FlowEngine(test_config)

        assert engine.config == test_config
        assert engine.current_procedure is None

    def test_load_procedure_success(self, test_config, temp_dir):
        """Test successful procedure loading"""
        sketch_file = temp_dir / "test_sketch.json"
        sketch_file.write_text(json.dumps(SIMPLE_SKETCH))

        engine = FlowEngine(test_config)
        result = engine.load_procedure(str(sketch_file))

        assert result is True
        assert engine.current_procedure is not None
        assert engine.current_procedure.name == "Test Procedure"

    def test_load_procedure_file_not_found(self, test_config):
        """Test procedure loading with non-existent file"""
        engine = FlowEngine(test_config)
        result = engine.load_procedure("/nonexistent/path.json")

        assert result is False
        assert engine.current_procedure is None

    def test_load_procedure_invalid_json(self, test_config, temp_dir):
        """Test procedure loading with invalid JSON"""
        sketch_file = temp_dir / "invalid_sketch.json"
        sketch_file.write_text("invalid json content")

        engine = FlowEngine(test_config)
        result = engine.load_procedure(str(sketch_file))

        assert result is False

    def test_start_procedure_no_procedure_loaded(self, test_config):
        """Test starting procedure without loading one first"""
        engine = FlowEngine(test_config)
        result = engine.start_procedure()

        assert result.success is False
        assert result.exit_code == 1
        assert "no procedure loaded" in result.message.lower()

    def test_pause_procedure(self, test_config):
        """Test procedure pausing"""
        engine = FlowEngine(test_config)
        # Set up initial state
        engine.state_manager.set_state(True, "started")

        result = engine.pause_procedure()

        assert result.success is True
        assert result.exit_code == 0
        assert "paused" in result.message.lower()

    def test_stop_procedure(self, test_config):
        """Test procedure stopping"""
        engine = FlowEngine(test_config)
        # Set up initial state
        engine.state_manager.set_state(True, "started")

        result = engine.stop_procedure()

        assert result.success is True
        assert result.exit_code == 0
        assert "stopped" in result.message.lower()

    def test_purge_data(self, test_config, temp_dir):
        """Test data purging"""
        # Create state and report files
        state_file = Path(test_config.state_file)
        report_file = Path(test_config.report_file)

        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("test state")
        report_file.write_text("test report")

        engine = FlowEngine(test_config)
        result = engine.purge_data()

        assert result.success is True
        assert not state_file.exists()
        assert not report_file.exists()

# CODE DUMP

#   @patch("flow_ctrl.src.core.engine.Procedure")
#   def test_start_procedure_success(self, mock_procedure_class, test_config, temp_dir):
#       """Test successful procedure start"""
#       sketch_file = temp_dir / "test_sketch.json"
#       sketch_file.write_text(json.dumps(SIMPLE_SKETCH))

#       mock_procedure = Mock()
#       mock_procedure.name = "Test Procedure"
#       mock_procedure.execute.return_value = True
#       mock_procedure_class.return_value = mock_procedure

#       engine = FlowEngine(test_config)
#       engine.load_procedure(str(sketch_file))
#       result = engine.start_procedure()

#       assert result.success is True
#       assert result.exit_code == 0
#       assert "successfully" in result.message.lower()


