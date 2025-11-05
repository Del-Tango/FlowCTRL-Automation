# ./flow_ctrl/src/utils/state_monitor.py
"""
State file monitoring for inter-process communication
"""

import time
import logging
import threading
from pathlib import Path
from typing import Callable, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StateMonitor:
    """Monitors state file for external commands and triggers callbacks"""

    def __init__(self, state_file: str, poll_interval: float = 1.0):
        self.state_file = Path(state_file)
        self.poll_interval = poll_interval
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.last_state = ""
        self.callbacks: Dict[str, Callable] = {}

    def register_callback(self, action: str, callback: Callable):
        """Register a callback for a specific action"""
        self.callbacks[action] = callback
        logger.debug(f"Registered callback for action: {action}")

    def start_monitoring(self):
        """Start monitoring the state file"""
        if self.monitoring:
            logger.warning("State monitor is already running")
            return

        self.monitoring = True
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"State monitor started (polling every {self.poll_interval}s)")

    def stop_monitoring(self):
        """Stop monitoring the state file"""
        if not self.monitoring:
            return

        self.monitoring = False
        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("State monitor stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set() and self.monitoring:
            try:
                self._check_state_changes()
                time.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in state monitor loop: {e}")
                time.sleep(self.poll_interval)

    def _check_state_changes(self):
        """Check for state file changes and trigger callbacks"""
        if not self.state_file.exists():
            return

        try:
            current_content = self.state_file.read_text().strip()
            if current_content == self.last_state:
                return

            # State has changed
            self.last_state = current_content

            if not current_content:
                # Empty state file - could be stop/purge command
                logger.debug("State file cleared")
                if "stop" in self.callbacks:
                    self.callbacks["stop"]()
                return

            # Parse state content
            fields = current_content.split(",")
            if len(fields) > 0:
                action = fields[0].lower()
                logger.debug(f"Detected state change: {action}")

                # Trigger appropriate callback
                if action in self.callbacks:
                    self.callbacks[action]()
                elif action in ["pause", "paused"] and "pause" in self.callbacks:
                    self.callbacks["pause"]()
                elif action in ["resume", "resumed"] and "resume" in self.callbacks:
                    self.callbacks["resume"]()
                elif action in ["stop", "stopped"] and "stop" in self.callbacks:
                    self.callbacks["stop"]()

        except Exception as e:
            logger.error(f"Error checking state changes: {e}")

    def send_command(self, command: str) -> bool:
        """Send a command to another process by writing to state file"""
        try:
            timestamp = datetime.now().isoformat()
            command_record = [command, "", "", "", timestamp]
            self.state_file.write_text(",".join(command_record))
            logger.debug(f"Sent command: {command}")
            return True
        except Exception as e:
            logger.error(f"Error sending command {command}: {e}")
            return False
