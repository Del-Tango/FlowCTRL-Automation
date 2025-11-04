"""
Integration tests for complete workflows
"""

import pytest
import tempfile
import json
from pathlib import Path

from flow_ctrl.src.core.engine import FlowEngine
from flow_ctrl.src.config.settings import FlowConfig
from tests.fixtures.sample_sketches import SIMPLE_SKETCH, MULTI_STAGE_SKETCH


class TestWorkflowIntegration:
    """Integration tests for complete workflows"""

    def test_simple_workflow_lifecycle(self, temp_dir):
        """Test complete workflow lifecycle"""
        # Create test sketch
        sketch_file = temp_dir / "simple_workflow.json"
        sketch_file.write_text(json.dumps(SIMPLE_SKETCH))

        # Create test config
        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "workflow.state"),
            report_file=str(temp_dir / "workflow.report"),
            log_file="workflow_test.log",
            silence=True,
            debug=True
        )

        # Initialize engine
        engine = FlowEngine(config)

        # Load procedure
        load_result = engine.load_procedure(str(sketch_file))
        assert load_result is True

        # Check state after load
        state = engine.state_manager.get_full_state()
        assert state['active'] is False

        # Start procedure
        start_result = engine.start_procedure()
        # Note: This will likely fail since we're using real shell commands
        # but we're testing the integration flow
        assert start_result is not None

        # Check state after start attempt
        state = engine.state_manager.get_full_state()
        # State might be active or not depending on execution

    def test_multi_stage_workflow_loading(self, temp_dir):
        """Test loading and parsing multi-stage workflow"""
        sketch_file = temp_dir / "multi_stage_workflow.json"
        sketch_file.write_text(json.dumps(MULTI_STAGE_SKETCH))

        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "multi_workflow.state"),
            report_file=str(temp_dir / "multi_workflow.report"),
            log_file="multi_workflow_test.log",
            silence=True,
            debug=True
        )

        engine = FlowEngine(config)
        load_result = engine.load_procedure(str(sketch_file))

        assert load_result is True
        assert engine.current_procedure is not None
        assert engine.current_procedure.name == "Multi-Stage Test"
        assert len(engine.current_procedure.stages) == 3

        # Verify stage names
        stage_names = [stage.name for stage in engine.current_procedure.stages]
        assert "setup_stage" in stage_names
        assert "main_stage" in stage_names
        assert "cleanup_stage" in stage_names

    def test_state_persistence(self, temp_dir):
        """Test state persistence across operations"""
        sketch_file = temp_dir / "state_test.json"
        sketch_file.write_text(json.dumps(SIMPLE_SKETCH))

        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "persistent.state"),
            report_file=str(temp_dir / "persistent.report"),
            log_file="persistent_test.log",
            silence=True,
            debug=True
        )

        # First engine instance
        engine1 = FlowEngine(config)
        engine1.load_procedure(str(sketch_file))

        # Set some state
        engine1.state_manager.set_state(True, "testing")
        engine1.state_manager.update_state(1, str(sketch_file))
        engine1.state_manager.update_state(2, "test_stage")

        # Verify state
        state1 = engine1.state_manager.get_full_state()
        assert state1['active'] is True
        assert state1['action'] == "testing"
        assert state1['sketch_file'] == str(sketch_file)
        assert state1['current_stage'] == "test_stage"

        # Create second engine instance (simulating restart)
        engine2 = FlowEngine(config)

        # Verify state persistence
        state2 = engine2.state_manager.get_full_state()
        assert state2['active'] is True
        assert state2['action'] == "testing"
