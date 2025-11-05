# ./flow_ctrl/tst/integration/test_state_control.py
"""
Integration tests for state-based inter-process control
"""

import pytest
import tempfile
import json
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from flow_ctrl.src.core.engine import FlowEngine
from flow_ctrl.src.core.procedure import Procedure
from flow_ctrl.src.config.settings import FlowConfig
from flow_ctrl.tst.fixtures.sample_sketches import SIMPLE_SKETCH


class TestStateControl:
    """Tests for state-based inter-process control"""

    def test_external_pause_resume_handlers(self, temp_dir):
        """Test pause and resume handler methods"""
        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "handlers.state"),
            report_file=str(temp_dir / "handlers.report"),
            log_file="handlers_test.log",
            silence=False,
            debug=True,
        )

        engine = FlowEngine(config)

        # Test pause handler
        engine._handle_external_pause()
        assert engine.execution_paused is True

        # Test resume handler
        engine._handle_external_resume()
        assert engine.execution_paused is False

        # Test stop handler
        engine._handle_external_stop()
        assert engine.execution_stopped is True

    def test_state_monitor_integration(self, temp_dir):
        """Test state monitor integration with engine"""
        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "monitor.state"),
            report_file=str(temp_dir / "monitor.report"),
            log_file="monitor_test.log",
            silence=False,
            debug=True,
        )

        engine = FlowEngine(config)

        # Verify state monitor was created and callbacks registered
        assert engine.state_monitor is not None
        assert "pause" in engine.state_monitor.callbacks
        assert "resume" in engine.state_monitor.callbacks
        assert "stop" in engine.state_monitor.callbacks

    def test_wait_if_paused(self, temp_dir):
        """Test the wait_if_paused method"""
        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "wait.state"),
            report_file=str(temp_dir / "wait.report"),
            log_file="wait_test.log",
            silence=False,
            debug=True,
        )

        engine = FlowEngine(config)

        # Test waiting while paused
        engine.execution_paused = True
        engine.execution_stopped = False

        # Start waiting in a separate thread
        wait_completed = [False]

        def wait_thread():
            try:
                engine._wait_if_paused()
                wait_completed[0] = True
            except Exception as e:
                wait_completed[0] = str(e)

        thread = threading.Thread(target=wait_thread)
        thread.start()

        # Let it wait for a bit
        time.sleep(0.5)
        assert not wait_completed[0]  # Should still be waiting

        # Resume and check it completes
        engine.execution_paused = False
        thread.join(timeout=1.0)
        assert wait_completed[0] is True

    def test_wait_if_paused_stopped(self, temp_dir):
        """Test wait_if_paused when stopped"""
        config = FlowConfig(
            project_dir=str(temp_dir),
            state_file=str(temp_dir / "wait_stop.state"),
            report_file=str(temp_dir / "wait_stop.report"),
            log_file="wait_stop_test.log",
            silence=False,
            debug=True,
        )

        engine = FlowEngine(config)

        # Test waiting while paused but then stopped
        engine.execution_paused = True
        engine.execution_stopped = False

        wait_result = [None]
        thread_completed = threading.Event()

        def wait_thread():
            try:
                engine._wait_if_paused()
                wait_result[0] = "completed"
            except Exception as e:
                wait_result[0] = str(e)
            finally:
                thread_completed.set()

        thread = threading.Thread(target=wait_thread)
        thread.daemon = True
        thread.start()

        # Give thread time to start
        time.sleep(0.1)

        # Stop the execution
        engine.execution_stopped = True

        # Wait for thread to complete with timeout
        thread_completed.wait(timeout=2.0)

        # Verify the result
        assert wait_result[0] is not None, "Wait thread did not complete"
        assert "stopped" in wait_result[0].lower(), f"Expected 'stopped' in result, got: {wait_result[0]}"

# CODE DUMP

#   @patch('flow_ctrl.src.core.engine.StateMonitor')
#   def test_external_stop_command(self, mock_state_monitor_class, temp_dir):
#       """Test stopping a procedure from external process"""
#       sketch_file = temp_dir / "control_test.json"
#       sketch_file.write_text(json.dumps(SIMPLE_SKETCH))

#       config = FlowConfig(
#           project_dir=str(temp_dir),
#           state_file=str(temp_dir / "control.state"),
#           report_file=str(temp_dir / "control.report"),
#           log_file="control_test.log",
#           silence=False,
#           debug=True,
#       )

#       # Mock the state monitor
#       mock_state_monitor = MagicMock()
#       mock_state_monitor_class.return_value = mock_state_monitor

#       # Create main engine
#       main_engine = FlowEngine(config)
#       main_engine.load_procedure(str(sketch_file))

#       # Replace the procedure execution with a controllable version
#       original_execute = main_engine._execute_with_control

#       def controllable_execute():
#           # Simulate long-running work that checks for stop signals
#           for i in range(10):
#               if main_engine.execution_stopped:
#                   ConsoleOutput.info("Stop detected in controllable execution")
#                   return False
#               time.sleep(0.1)
#           return True

#       main_engine._execute_with_control = controllable_execute

#       # Start execution in separate thread
#       execution_result = [None]

#       def run_main():
#           execution_result[0] = main_engine.start_procedure()

#       main_thread = threading.Thread(target=run_main)
#       main_thread.start()

#       # Give main process time to start
#       time.sleep(0.5)

#       # Simulate external stop command by directly calling the handler
#       main_engine._handle_external_stop()

#       # Wait for main thread to finish
#       main_thread.join(timeout=3.0)

#       # Verify main process received stop command
#       assert main_engine.execution_stopped is True
#       assert execution_result[0] is not None
#       assert execution_result[0].success is False
#       assert "stopped" in execution_result[0].message.lower()

