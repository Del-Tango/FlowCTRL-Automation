"""

Procedure representation and execution logic
"""

import os
import logging
import pysnooper

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .stage import Stage, StageStats
from ..utils.state_manager import StateManager  # FIX: Correct import path

logger = logging.getLogger(__name__)


@dataclass
class ProcedureStats:
    """Procedure execution statistics"""

    total_stages: int = 0
    completed_stages: int = 0
    total_actions: int = 0
    completed_actions: int = 0
    success_count: int = 0
    failure_count: int = 0


class Procedure:
    """Represents a complete automation procedure"""

    def __init__(self, data: Dict[str, Any], config, sketch_file=None):
        self.data = data
        self.config = config
        self.name = data.get(
            "name",
            "Unamed procedure" if not sketch_file else os.path.basename(sketch_file),
        )
        self.stages: List[Stage] = []
        self.state_manager = StateManager(config.state_file)
        self.stats = ProcedureStats(0, 0, 0, 0, 0, 0)

        # Add configuration for failure handling
        self.continue_on_failure = data.get("continue_on_failure", True)
        self.max_failures = data.get("max_failures", 0)  # 0 means unlimited
        self.failure_count = 0

        self._parse_stages()

    def _parse_stages(self):
        """Parse stages from procedure data"""
        for stage_name, actions_data in self.data.items():
            if stage_name == "name":
                continue

            stage = Stage(stage_name, actions_data, self.config)
            self.stages.append(stage)
            self.stats.total_stages += 1
            self.stats.total_actions += len(actions_data)

    # @pysnooper.snoop()
    def execute(self) -> bool:
        """Execute the complete procedure"""
        logger.info(f"Executing procedure: {self.name}")
        self.failure_count = 0  # Reset failure count

        try:
            for stage in self.stages:
                self.state_manager.update_state(2, stage.name)  # Record current stage

                logger.info(f"Processing stage: {stage.name}")
                stage_success = stage.execute()

                if stage_success:
                    self.stats.completed_stages += 1
                    self.stats.success_count += 1
                    logger.info(f"Stage completed successfully: {stage.name}")
                else:
                    self.stats.failure_count += 1
                    self.failure_count += 1
                    logger.error(f"Stage failed: {stage.name}")

                    # Check if we should continue on failure
                    if not self._should_continue_on_failure():
                        logger.error(
                            f"Condition fatal after stage {stage.name} failure! Terminating"
                        )
                        return False

            # Final cleanup
            self._cleanup()

            success = self.stats.failure_count == 0
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"Procedure completed: {status}")

            # Log detailed statistics
            logger.info(
                f"Procedure statistics: {self.stats.completed_stages}/{self.stats.total_stages} stages completed, "
                f"{self.stats.success_count} successes, {self.stats.failure_count} failures"
            )

            return success

        except Exception as e:
            logger.error(f"Procedure execution error: {e}")
            # Always attempt cleanup even on error
            try:
                self._cleanup()
            except Exception as cleanup_error:
                logger.error(f"Error during emergency cleanup: {cleanup_error}")
            return False

    def _should_continue_on_failure(self) -> bool:
        """Determine if procedure should continue after failure"""
        # Check if we've exceeded maximum allowed failures
        if self.max_failures > 0 and self.failure_count >= self.max_failures:
            logger.warning(
                f"Maximum failures ({self.max_failures}) reached, terminating procedure"
            )
            return False

        # Return the procedure-level configuration
        return self.continue_on_failure

    def _cleanup(self):
        """Cleanup after procedure execution"""
        try:
            logger.info("Performing procedure cleanup...")

            # Execute any procedure-level cleanup commands
            if "cleanup" in self.data:
                cleanup_commands = self.data["cleanup"]
                if isinstance(cleanup_commands, list):
                    for cmd_data in cleanup_commands:
                        self._execute_cleanup_command(cmd_data)
                elif isinstance(cleanup_commands, dict):
                    self._execute_cleanup_command(cleanup_commands)

            # Reset state to inactive
            self.state_manager.set_state(False, "completed")

            logger.info("Procedure cleanup completed")

        except Exception as e:
            logger.error(f"Error during procedure cleanup: {e}")

    def _execute_cleanup_command(self, cmd_data: Dict[str, Any]):
        """Execute a single cleanup command"""
        try:
            if "cmd" not in cmd_data:
                return

            cmd_name = cmd_data.get("name", "unnamed_cleanup")
            command = cmd_data["cmd"]

            logger.info(f"Executing cleanup command: {cmd_name}")

            # Use ShellExecutor to execute the command
            from ..utils.shell import ShellExecutor

            executor = ShellExecutor()
            result = executor.execute(command)

            if result.exit_code == 0:
                logger.info(f"Cleanup command '{cmd_name}' completed successfully")
            else:
                logger.warning(
                    f"Cleanup command '{cmd_name}' failed with exit code {result.exit_code}"
                )

        except Exception as e:
            logger.error(f"Error executing cleanup command: {e}")

    def get_progress(self) -> Dict[str, Any]:
        """Get current execution progress"""
        return {
            "name": self.name,
            "current_stage": (
                self.state_manager.get_state_field(2)
                if self.state_manager.get_state()
                else None
            ),
            "stats": {
                "total_stages": self.stats.total_stages,
                "completed_stages": self.stats.completed_stages,
                "total_actions": self.stats.total_actions,
                "completed_actions": self.stats.completed_actions,
                "success_count": self.stats.success_count,
                "failure_count": self.stats.failure_count,
            },
        }
