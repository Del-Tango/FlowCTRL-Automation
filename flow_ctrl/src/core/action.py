"""
Action representation and execution logic
"""

import logging
import time

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from threading import Thread, Event

from ..utils.shell import ShellExecutor
from ..utils.state_manager import StateManager
from ..utils.logger import ConsoleOutput
from ..config.settings import TIME_MULTIPLIERS

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of command execution"""

    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float


class Action:
    """Represents a single automation action"""

    def __init__(self, data: Dict[str, Any], config):
        self.data = data
        self.config = config
        self.name = data.get("name", "Unnamed Action")
        self.command = data.get("cmd", "")
        self.setup_command = data.get("setup-cmd", "")
        self.teardown_command = data.get("teardown-cmd", "")
        self.on_ok_command = data.get("on-ok-cmd", "")
        self.on_nok_command = data.get("on-nok-cmd", "")
        self.fatal_nok = data.get("fatal-nok", False)
        self.timeout = self._parse_time(data.get("timeout", ""))
        self.estimated_time = self._parse_time(data.get("time", ""))

        # FIX: Remove non-existent handler
        # self.handler = ActionHandler(config)
        self.shell = ShellExecutor()
        self.state_manager = StateManager(config.state_file)

    def _parse_time(self, time_str: str) -> Optional[int]:
        """Parse time string to seconds"""
        if not time_str:
            return None

        try:
            unit = time_str[-1].lower()
            value = int(time_str[:-1])

            if unit in TIME_MULTIPLIERS:
                return value * TIME_MULTIPLIERS[unit]
            else:
                logger.warning(f"Unknown time unit: {unit} in {time_str}")
                return value
        except (ValueError, IndexError):
            logger.warning(f"Invalid time format: {time_str}")
            return None

    def execute(self) -> bool:
        """Execute the action with all associated commands"""
        ConsoleOutput.info(f'Executing Procedure Stage Action: {self.name}')
        logger.info(f"Executing action: {self.name}")

        try:
            # Execute setup command
            if self.setup_command:
                setup_result = self._execute_command(self.setup_command, "setup")
                if not setup_result.success:
                    logger.warning(f"Setup command failed for action: {self.name}")

            # Execute main command
            main_result = self._execute_command(self.command, "main")

            # Execute appropriate follow-up command
            if main_result.success and self.on_ok_command:
                self._execute_command(self.on_ok_command, "on-ok")
            elif not main_result.success and self.on_nok_command:
                self._execute_command(self.on_nok_command, "on-nok")

            # Execute teardown command
            if self.teardown_command:
                teardown_result = self._execute_command(
                    self.teardown_command, "teardown"
                )
                if not teardown_result.success:
                    logger.warning(f"Teardown command failed for action: {self.name}")

            logger.info(
                f"Action completed: {self.name} - {'SUCCESS' if main_result.success else 'FAILED'}"
            )
            return main_result.success

        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return False

    def _execute_command(self, command: str, command_type: str) -> CommandResult:
        """Execute a shell command with timeout support"""
        if not command:
            return CommandResult(True, "", "", 0, 0.0)

        logger.info(f"Executing {command_type} command: {command}")

        start_time = time.time()

        try:
            if self.timeout:
                result = self.shell.execute_with_timeout(command, self.timeout)
            else:
                result = self.shell.execute(command)

            execution_time = time.time() - start_time

            if result.exit_code == 0:
                logger.info(
                    f"{command_type} command succeeded in {execution_time:.2f}s"
                )
            else:
                logger.warning(
                    f"{command_type} command failed with exit code {result.exit_code}"
                )
                if result.stderr:
                    logger.error(f"Command stderr: {result.stderr}")

            return CommandResult(
                success=result.exit_code == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.exit_code,
                execution_time=execution_time,
            )

        except TimeoutError:
            execution_time = time.time() - start_time
            logger.error(
                f"{command_type} command timed out after {execution_time:.2f}s"
            )
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {self.timeout}s",
                exit_code=124,
                execution_time=execution_time,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{command_type} command execution error: {e}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=1,
                execution_time=execution_time,
            )

    def validate(self) -> bool:
        """Validate action configuration"""
        if not self.command:
            logger.error(f"Action {self.name} has no command")
            return False

        if self.timeout is not None and self.timeout <= 0:
            logger.error(f"Action {self.name} has invalid timeout: {self.timeout}")
            return False

        return True
