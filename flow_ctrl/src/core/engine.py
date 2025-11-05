"""
Main Flow-CTRL engine coordinating procedure execution
"""

import os
import logging
import json
import pysnooper

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .procedure import Procedure
from .validator import Validator
from ..utils.state_manager import StateManager
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
    """Main engine coordinating automation workflows"""

    def __init__(self, config):
        self.config = config
        self.validator = Validator()
        self.state_manager = StateManager(config.state_file)
        self.current_procedure: Optional[Procedure] = None
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        setup_logging(
            log_file=Path(self.config.project_dir)
            / self.config.log_dir
            / self.config.log_file,
            log_name=self.config.log_name,
            log_format=self.config.log_format,
            timestamp_format=self.config.timestamp_format,
            debug_mode=self.config.debug,
        )

    def load_procedure(self, sketch_file: str) -> bool:
        """Load a procedure from sketch file"""
        ConsoleOutput.info(f'Loading sketch file: {sketch_file}')
        try:
            sketch_path = Path(sketch_file)
            if not sketch_path.exists():
                logger.error(f"Sketch file not found: {sketch_file}")
                return False

            with open(sketch_path, "r") as f:
                procedure_data = json.load(f)

            if not self.validator.validate_instruction(procedure_data):
                logger.error("Invalid procedure sketch")
                return False

            self.current_procedure = Procedure(procedure_data, self.config, sketch_file)
            self.state_manager.update_state(1, sketch_file)  # Record sketch file

            logger.info(f"Loaded procedure from: {sketch_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to load procedure: {e}")
            return False

    # @pysnooper.snoop()
    def start_procedure(self) -> ExecutionResult:
        """Start procedure execution"""
        ConsoleOutput.info('Starting procedure')
        if not self.current_procedure:
            return ExecutionResult(
                success=False, message="No procedure loaded", exit_code=1, details={}
            )

        # Get current state and previous action for validation
        current_state = self.state_manager.get_state()
        previous_action = self.state_manager.get_state_field(0) or ""

        if not self.validator.validate_state(current_state, previous_action, "start"):
            return ExecutionResult(
                success=False,
                message="Invalid state for start action",
                exit_code=1,
                details={"state": current_state, "previous_action": previous_action},
            )

        try:
            self.state_manager.set_state(True, "started")
            logger.info("Starting procedure execution")

            success = self.current_procedure.execute()

            if success:
                message = "Procedure completed successfully"
                exit_code = 0
            else:
                message = "Procedure execution failed"
                exit_code = 1

            return ExecutionResult(
                success=success,
                message=message,
                exit_code=exit_code,
                details={"procedure": self.current_procedure.name},
            )

        except Exception as e:
            logger.error(f"Procedure execution error: {e}")
            return ExecutionResult(
                success=False,
                message=f"Execution error: {e}",
                exit_code=2,
                details={"error": str(e)},
            )

    def pause_procedure(self) -> ExecutionResult:
        """Pause current procedure"""
        ConsoleOutput.info(f'Pausing procedure: {self.current_procedure}')
        current_state = self.state_manager.get_state()
        previous_action = self.state_manager.get_state_field(0) or ""

        if not self.validator.validate_state(current_state, previous_action, "pause"):
            return ExecutionResult(
                success=False,
                message="Invalid state for pause action",
                exit_code=1,
                details={"state": current_state, "previous_action": previous_action},
            )

        self.state_manager.set_state(True, "paused")
        logger.info("Procedure paused")

        return ExecutionResult(
            success=True,
            message="Procedure paused",
            exit_code=0,
            details={"state": "paused"},
        )

    def resume_procedure(self) -> ExecutionResult:
        """Resume paused procedure"""
        ConsoleOutput.info(f'Resuming procedure: {self.current_procedure}')
        current_state = self.state_manager.get_state()
        previous_action = self.state_manager.get_state_field(0) or ""

        if not self.validator.validate_state(current_state, previous_action, "resume"):
            return ExecutionResult(
                success=False,
                message="Invalid state for resume action",
                exit_code=1,
                details={"state": current_state, "previous_action": previous_action},
            )

        self.state_manager.set_state(True, "resumed")
        logger.info("Procedure resumed")

        # Implementation would resume from last state
        return ExecutionResult(
            success=True,
            message="Procedure resumed",
            exit_code=0,
            details={"state": "resumed"},
        )

    def stop_procedure(self) -> ExecutionResult:
        """Stop current procedure"""
        ConsoleOutput.info(f'Stopping procedure: {self.current_procedure}')
        current_state = self.state_manager.get_state()
        previous_action = self.state_manager.get_state_field(0) or ""

        if not self.validator.validate_state(current_state, previous_action, "stop"):
            return ExecutionResult(
                success=False,
                message="Invalid state for stop action",
                exit_code=1,
                details={"state": current_state, "previous_action": previous_action},
            )

        self.state_manager.set_state(False, "stopped")
        logger.info("Procedure stopped")

        return ExecutionResult(
            success=True,
            message="Procedure stopped",
            exit_code=0,
            details={"state": "stopped"},
        )

    def purge_data(self) -> ExecutionResult:
        """Purge all state and report data"""
        ConsoleOutput.info('Purging all state and report data')
        try:
            self.state_manager.purge()

            # Clear report file
            report_path = Path(self.config.report_file)
            if report_path.exists():
                report_path.unlink()

            logger.info("All data purged")
            return ExecutionResult(
                success=True, message="All data purged", exit_code=0, details={}
            )

        except Exception as e:
            logger.error(f"Purge error: {e}")
            return ExecutionResult(
                success=False,
                message=f"Purge failed: {e}",
                exit_code=1,
                details={"error": str(e)},
            )


# CODE DUMP
