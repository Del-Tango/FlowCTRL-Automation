"""
Main Flow-CTRL engine coordinating procedure execution with state monitoring
"""

import os
import logging
import json
import time
import threading

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .procedure import Procedure, ProcedureStats
from .stage import Stage, StageStats
from .validator import Validator
from ..utils.state_manager import StateManager
from ..utils.state_monitor import StateMonitor
from ..utils.logger import setup_logging, ConsoleOutput

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of procedure execution"""

    success: bool
    message: str
    exit_code: int
    details: Dict[str, Any]


class FlowEngine:
    """Main engine coordinating automation workflows with state monitoring"""

    def __init__(self, config):
        self.config = config
        self.validator = Validator()
        self.state_manager = StateManager(config.state_file)
        self.state_monitor = StateMonitor(config.state_file, poll_interval=0.5)
        self.current_procedure: Optional[Procedure] = None
        self.execution_paused = False
        self.execution_stopped = False
        self._setup_logging()
        self._setup_state_monitoring()

    def _setup_logging(self):
        """Setup logging configuration"""
        # Ensure log directory exists
        log_dir = Path(self.config.project_dir) / self.config.log_dir
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / self.config.log_file

        self.logger = setup_logging(
            log_file=log_file,
            log_name=self.config.log_name,
            log_format=self.config.log_format,
            timestamp_format=self.config.timestamp_format,
            debug_mode=self.config.debug,
        )

        ConsoleOutput.info(f"Logging configured: {log_file}")

    def _setup_state_monitoring(self):
        """Setup state monitoring for inter-process communication"""
        # Register callbacks for external commands
        self.state_monitor.register_callback("pause", self._handle_external_pause)
        self.state_monitor.register_callback("resume", self._handle_external_resume)
        self.state_monitor.register_callback("stop", self._handle_external_stop)

        ConsoleOutput.info("State monitoring configured for inter-process control")

    def _handle_external_pause(self):
        """Handle external pause command"""
        if not self.execution_paused and not self.execution_stopped:
            ConsoleOutput.info("External PAUSE command received")
            self.execution_paused = True
            # Update state to reflect pause
            self.state_manager.set_state(True, "paused")

    def _handle_external_resume(self):
        """Handle external resume command"""
        if self.execution_paused and not self.execution_stopped:
            ConsoleOutput.info("External RESUME command received")
            self.execution_paused = False
            # Update state to reflect resume
            self.state_manager.set_state(True, "resumed")

    def _handle_external_stop(self):
        """Handle external stop command"""
        if not self.execution_stopped:
            ConsoleOutput.info("External STOP command received")
            self.execution_stopped = True
            self.execution_paused = False
            # State will be cleared by stop_procedure

    def _wait_if_paused(self):
        """Wait if execution is paused, checking for resume/stop commands"""
        while self.execution_paused and not self.execution_stopped:
            ConsoleOutput.info("Execution paused - waiting for resume...")
            time.sleep(1)  # Check every second

        if self.execution_stopped:
            raise Exception("Execution stopped by external command")

    def load_procedure(self, sketch_file: str) -> bool:
        """Load a procedure from sketch file"""
        ConsoleOutput.info(f"Loading sketch file: {sketch_file}")
        try:
            sketch_path = Path(sketch_file)
            if not sketch_path.exists():
                ConsoleOutput.error(f"Sketch file not found: {sketch_file}")
                logger.error(f"Sketch file not found: {sketch_file}")
                return False

            with open(sketch_path, "r") as f:
                procedure_data = json.load(f)

            if not self.validator.validate_instruction(procedure_data):
                ConsoleOutput.error("Invalid procedure sketch")
                logger.error("Invalid procedure sketch")
                return False

            self.current_procedure = Procedure(procedure_data, self.config, sketch_file)
            self.state_manager.update_state(1, sketch_file)  # Record sketch file

            ConsoleOutput.ok(f"Loaded procedure: {self.current_procedure.name}")
            logger.info(f"Loaded procedure from: {sketch_file}")
            return True

        except Exception as e:
            ConsoleOutput.error(f"Failed to load procedure: {e}")
            logger.error(f"Failed to load procedure: {e}")
            return False

    def start_procedure(self) -> ExecutionResult:
        """Start procedure execution with state monitoring"""
        ConsoleOutput.info("Starting procedure execution with state monitoring")
        if not self.current_procedure:
            msg = "No procedure loaded"
            ConsoleOutput.error(msg)
            return ExecutionResult(success=False, message=msg, exit_code=1, details={})

        # Get current state and previous action for validation
        current_state = self.state_manager.get_state()
        previous_action = self.state_manager.get_state_field(0) or ""

        if not self.validator.validate_state(current_state, previous_action, "start"):
            msg = "Invalid state for start action"
            ConsoleOutput.error(msg)
            return ExecutionResult(
                success=False,
                message=msg,
                exit_code=1,
                details={"state": current_state, "previous_action": previous_action},
            )

        try:
            # Reset control flags
            self.execution_paused = False
            self.execution_stopped = False

            # Start state monitoring
            self.state_monitor.start_monitoring()

            self.state_manager.set_state(True, "started")
            ConsoleOutput.info("Procedure state set to STARTED")
            ConsoleOutput.info(
                "State monitoring active - process can be controlled externally"
            )
            logger.info("Starting procedure execution with state monitoring")

            # Modified execution that respects pause/stop commands
            success = self._execute_with_control()

            if success:
                message = "Procedure finalized successfuly!"
                exit_code = 0
            else:
                if self.execution_stopped:
                    message = "Procedure stopped by external command"
                    ConsoleOutput.warning(message)
                else:
                    message = "Procedure execution failed"
                    ConsoleOutput.nok(message)
                exit_code = 1

            # Stop state monitoring
            self.state_monitor.stop_monitoring()

            return ExecutionResult(
                success=success and not self.execution_stopped,
                message=message,
                exit_code=exit_code,
                details={"procedure": self.current_procedure.name},
            )

        except Exception as e:
            error_msg = f"Procedure execution error: {e}"
            ConsoleOutput.error(error_msg)
            logger.error(error_msg)
            # Ensure monitoring is stopped on error
            self.state_monitor.stop_monitoring()
            return ExecutionResult(
                success=False,
                message=error_msg,
                exit_code=2,
                details={"error": str(e)},
            )

    def _execute_with_control(self) -> bool:
        """Execute procedure with pause/stop control"""
        try:
            ConsoleOutput.info("Beginning controlled procedure execution...")

            if not self.current_procedure or not hasattr(
                self.current_procedure, "stages"
            ):
                ConsoleOutput.error("No valid procedure to execute")
                return False

            # Reset procedure statistics
            self.current_procedure.stats = ProcedureStats(
                total_stages=len(self.current_procedure.stages),
                completed_stages=0,
                total_actions=sum(
                    len(stage.actions) for stage in self.current_procedure.stages
                ),
                completed_actions=0,
                success_count=0,
                failure_count=0,
            )

            for stage in self.current_procedure.stages:
                # Check for stop/pause before each stage
                if self.execution_stopped:
                    ConsoleOutput.info("Stop command detected - terminating execution")
                    return False

                self._wait_if_paused()

                self.state_manager.update_state(2, stage.name)
                ConsoleOutput.info(f"Processing stage: {stage.name}")

                # Execute stage with control
                stage_success = self._execute_stage_with_control(stage)

                if stage_success:
                    self.current_procedure.stats.completed_stages += 1
                    self.current_procedure.stats.success_count += 1
                    ConsoleOutput.ok(f"Stage completed: {stage.name}")
                else:
                    self.current_procedure.stats.failure_count += 1
                    ConsoleOutput.nok(f"Stage failed: {stage.name}")

                    if not self._should_continue_on_stage_failure():
                        ConsoleOutput.error(
                            f"Stage failed, terminating procedure: {stage.name}"
                        )
                        return False

            success = (
                self.current_procedure.stats.failure_count == 0
                and not self.execution_stopped
            )
            if success:
                ConsoleOutput.ok("Procedure completed: SUCCESS")
            elif self.execution_stopped:
                ConsoleOutput.warning("Procedure stopped by external command")
            else:
                ConsoleOutput.nok("Procedure completed: FAILED")

            return success

        except Exception as e:
            ConsoleOutput.error(f"Controlled execution error: {e}")
            return False

    def _execute_stage_with_control(self, stage) -> bool:
        """Execute a single stage with pause/stop control"""
        try:
            if not hasattr(stage, "actions"):
                ConsoleOutput.error(f"Stage {stage.name} has no actions")
                return False

            # Reset stage statistics
            stage.stats = StageStats(
                total_actions=len(stage.actions),
                completed_actions=0,
                success_count=0,
                failure_count=0,
            )

            for action in stage.actions:
                # Check for stop/pause before each action
                if self.execution_stopped:
                    ConsoleOutput.info("Stop command detected during action execution")
                    return False

                self._wait_if_paused()

                self.state_manager.update_state(3, action.name)
                ConsoleOutput.info(f"Processing action: {action.name}")

                # Execute the action
                action_success = action.execute()

                if action_success:
                    stage.stats.completed_actions += 1
                    stage.stats.success_count += 1
                    ConsoleOutput.ok(f"Action completed: {action.name}")
                else:
                    stage.stats.failure_count += 1
                    ConsoleOutput.nok(f"Action failed: {action.name}")

                    if not self._should_continue_on_action_failure(action):
                        ConsoleOutput.error(
                            f"Action failed, terminating stage: {action.name}"
                        )
                        return False

            return stage.stats.failure_count == 0

        except Exception as e:
            ConsoleOutput.error(f"Stage execution error: {e}")
            return False

    def pause_procedure(self) -> ExecutionResult:
        """Pause current procedure - can be called externally"""
        ConsoleOutput.info("Pausing procedure")
        current_state = self.state_manager.get_state()
        previous_action = self.state_manager.get_state_field(0) or ""

        if not self.validator.validate_state(current_state, previous_action, "pause"):
            return ExecutionResult(
                success=False,
                message="Invalid state for pause action",
                exit_code=1,
                details={"state": current_state, "previous_action": previous_action},
            )

        self.execution_paused = True
        self.state_manager.set_state(True, "paused")
        ConsoleOutput.info("Procedure paused")
        logger.info("Procedure paused")

        return ExecutionResult(
            success=True,
            message="Procedure paused",
            exit_code=0,
            details={"state": "paused"},
        )

    def resume_procedure(self) -> ExecutionResult:
        """Resume paused procedure - can be called externally"""
        ConsoleOutput.info("Resuming procedure")
        current_state = self.state_manager.get_state()
        previous_action = self.state_manager.get_state_field(0) or ""

        if not self.validator.validate_state(current_state, previous_action, "resume"):
            return ExecutionResult(
                success=False,
                message="Invalid state for resume action",
                exit_code=1,
                details={"state": current_state, "previous_action": previous_action},
            )

        self.execution_paused = False
        self.state_manager.set_state(True, "resumed")
        ConsoleOutput.info("Procedure resumed")
        logger.info("Procedure resumed")

        return ExecutionResult(
            success=True,
            message="Procedure resumed",
            exit_code=0,
            details={"state": "resumed"},
        )

    def stop_procedure(self) -> ExecutionResult:
        """Stop current procedure - can be called externally"""
        ConsoleOutput.info("Stopping procedure")
        current_state = self.state_manager.get_state()
        previous_action = self.state_manager.get_state_field(0) or ""

        if not self.validator.validate_state(current_state, previous_action, "stop"):
            return ExecutionResult(
                success=False,
                message="Invalid state for stop action",
                exit_code=1,
                details={"state": current_state, "previous_action": previous_action},
            )

        self.execution_stopped = True
        self.execution_paused = False
        self.state_manager.set_state(False, "stopped")
        ConsoleOutput.info("Procedure stopped")
        logger.info("Procedure stopped")

        return ExecutionResult(
            success=True,
            message="Procedure stopped",
            exit_code=0,
            details={"state": "stopped"},
        )

    def send_external_command(self, command: str) -> bool:
        """Send a command to a running Flow-CTRL process"""
        ConsoleOutput.info(f"Sending external command: {command}")
        return self.state_manager.send_command(command)

    def purge_data(self) -> ExecutionResult:
        """Purge all state and report data"""
        ConsoleOutput.info("Purging all state and report data")
        try:
            # Stop monitoring if running
            self.state_monitor.stop_monitoring()

            self.state_manager.purge()

            # Clear report file
            report_path = Path(self.config.report_file)
            if report_path.exists():
                report_path.unlink()

            ConsoleOutput.ok("All data purged")
            logger.info("All data purged")
            return ExecutionResult(
                success=True, message="All data purged", exit_code=0, details={}
            )

        except Exception as e:
            ConsoleOutput.error(f"Purge error: {e}")
            logger.error(f"Purge error: {e}")
            return ExecutionResult(
                success=False,
                message=f"Purge failed: {e}",
                exit_code=1,
                details={"error": str(e)},
            )

    def _should_continue_on_stage_failure(self) -> bool:
        """Determine if execution should continue after stage failure"""
        # Check procedure-level configuration if available
        if self.current_procedure and hasattr(
            self.current_procedure, "_should_continue_on_failure"
        ):
            return self.current_procedure._should_continue_on_failure()

        # Default behavior: continue unless explicitly configured to stop
        # This allows procedures to define their own failure handling logic
        return True

    def _should_continue_on_action_failure(self, action) -> bool:
        """Determine if stage should continue after action failure"""
        # First check if action is marked as fatal
        if getattr(action, "fatal_nok", False):
            return False

        # Then check procedure-level configuration
        if self.current_procedure and hasattr(
            self.current_procedure, "_should_continue_on_failure"
        ):
            return self.current_procedure._should_continue_on_failure()

        # Default: continue on action failure
        return True

# CODE DUMP
