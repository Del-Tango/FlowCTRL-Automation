"""
Shell command execution utilities
"""

import subprocess
import threading
import time
import logging

from typing import NamedTuple, List, Optional
from dataclasses import dataclass
from ..utils.logger import ConsoleOutput

logger = logging.getLogger(__name__)


class CommandResult(NamedTuple):
    """Result of command execution"""

    stdout: str
    stderr: str
    exit_code: int


@dataclass
class TimeoutResult:
    """Result for timed-out command"""

    stdout: str = ""
    stderr: str = "Command timed out"
    exit_code: int = 124


class ShellExecutor:
    """Executes shell commands with timeout and thread support"""

    def execute(self, command: str, user: Optional[str] = None) -> CommandResult:
        """Execute a shell command"""
        try:
            if user:
                command = f"su {user} -c '{command}'"

            ConsoleOutput.banner(f"CMD> {command}")
            logger.debug(f"Executing command: {command}")

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            stdout, stderr = process.communicate()
            exit_code = process.returncode

            # Remove trailing newlines
            stdout = stdout.rstrip("\n")
            stderr = stderr.rstrip("\n")

            ConsoleOutput.banner(stdout + "\n")
            if exit_code != 0:
                ConsoleOutput.nok(stderr + "\n")

            logger.debug(
                f"Command result - Exit: {exit_code}, Stdout: {stdout[:100]}, Stderr: {stderr[:100]}"
            )

            return CommandResult(stdout, stderr, exit_code)

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return CommandResult("", str(e), 1)

    def execute_with_timeout(
        self, command: str, timeout: int, user: Optional[str] = None
    ) -> CommandResult:
        """Execute command with timeout"""
        result_container = []
        stop_event = threading.Event()

        def _execute():
            try:
                result = self.execute(command, user)
                result_container.append(result)
            except Exception as e:
                result_container.append(CommandResult("", str(e), 1))
            finally:
                stop_event.set()

        # Start execution thread
        thread = threading.Thread(target=_execute)
        thread.daemon = True
        thread.start()

        # Wait for completion or timeout
        thread.join(timeout)

        if thread.is_alive():
            # Command timed out
            logger.warning(f"Command timed out after {timeout}s: {command}")
            stop_event.set()
            return TimeoutResult()
        else:
            # Command completed
            return (
                result_container[0]
                if result_container
                else CommandResult("", "Unknown error", 1)
            )

    def execute_detached(self, command: str, user: Optional[str] = None) -> int:
        """Execute command in detached mode (non-blocking)"""
        try:
            if user:
                command = f"su {user} -c '{command}'"

            # Add nohup and background execution
            detached_command = f"nohup {command} > /dev/null 2>&1 &"

            process = subprocess.Popen(
                detached_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            process.wait()
            return process.returncode

        except Exception as e:
            logger.error(f"Detached command execution error: {e}")
            return 1

    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in system PATH"""
        try:
            result = subprocess.run(
                ["which", command], capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False
