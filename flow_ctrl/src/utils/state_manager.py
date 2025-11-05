# ./flow_ctrl/src/utils/state_manager.py
"""
State management for procedure execution with command support
"""

import csv
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """Manages procedure execution state with command capabilities"""

    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self._ensure_state_file()

    def _ensure_state_file(self):
        """Ensure state file exists"""
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.touch()

    def _read_state_record(self) -> List[str]:
        """Read current state record from file"""
        try:
            if not self.state_file.exists() or self.state_file.stat().st_size == 0:
                return [""] * 5  # Return empty record

            content = self.state_file.read_text().strip()
            if not content:
                return [""] * 5

            fields = content.split(",")
            # Ensure we have exactly 5 fields
            while len(fields) < 5:
                fields.append("")
            return fields[:5]  # Return only first 5 fields
        except Exception as e:
            logger.error(f"Error reading state record: {e}")
            return [""] * 5

    def _write_state_record(self, state_record: List[str]) -> bool:
        """Write state record to file"""
        try:
            # Ensure we have exactly 5 fields
            while len(state_record) < 5:
                state_record.append("")
            state_record = state_record[:5]

            # Always update timestamp in field 4
            state_record[4] = datetime.now().isoformat()

            self.state_file.write_text(",".join(state_record))
            return True
        except Exception as e:
            logger.error(f"Error writing state record: {e}")
            return False

    def set_state(self, active: bool, action: str) -> bool:
        """Set overall procedure state"""
        try:
            if not active:
                # Clear state file when deactivating - this signals STOP to other processes
                self.state_file.write_text("")
                logger.debug("State cleared (STOP command)")
                return True

            # Read existing state to preserve fields 1-3
            current_state = self._read_state_record()

            # Update only action and timestamp, preserve other fields
            state_record = [
                action,  # Current action (field 0)
                current_state[1] if len(current_state) > 1 else "",  # Sketch file (field 1)
                current_state[2] if len(current_state) > 2 else "",  # Current stage (field 2)
                current_state[3] if len(current_state) > 3 else "",  # Current action (field 3)
                datetime.now().isoformat(),  # Timestamp (field 4)
            ]

            return self._write_state_record(state_record)

        except Exception as e:
            logger.error(f"Error setting state: {e}")
            return False

    def send_command(self, command: str) -> bool:
        """Send a command to the main process"""
        try:
            # Read existing state to preserve current context
            current_state = self._read_state_record()

            # Create command record preserving existing context
            command_record = [
                command,  # Command as action (field 0)
                current_state[1] if len(current_state) > 1 else "",  # Preserve sketch file
                current_state[2] if len(current_state) > 2 else "",  # Preserve current stage
                current_state[3] if len(current_state) > 3 else "",  # Preserve current action
                datetime.now().isoformat(),  # Update timestamp
            ]

            return self._write_state_record(command_record)

        except Exception as e:
            logger.error(f"Error sending command {command}: {e}")
            return False

    def get_state(self) -> bool:
        """Check if procedure is active"""
        return self.state_file.exists() and self.state_file.stat().st_size > 0

    def get_state_field(self, field_index: int) -> Optional[str]:
        """Get specific field from state record"""
        try:
            if not self.get_state():
                return None

            content = self.state_file.read_text().strip()
            if not content:
                return None

            fields = content.split(",")
            if field_index < len(fields):
                return fields[field_index]
            else:
                return None

        except Exception as e:
            logger.error(f"Error reading state field: {e}")
            return None

    def update_state(self, field_index: int, value: str) -> bool:
        """Update specific field in state record"""
        try:
            # Read existing state
            state_record = self._read_state_record()

            # Validate field index
            if field_index < 0 or field_index >= len(state_record):
                logger.error(f"Invalid field index: {field_index}")
                return False

            # Update the specific field
            state_record[field_index] = value

            return self._write_state_record(state_record)

        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return False

    def get_full_state(self) -> Dict[str, Any]:
        """Get complete state information"""
        if not self.get_state():
            return {"active": False}

        try:
            content = self.state_file.read_text().strip()
            fields = content.split(",")

            return {
                "active": True,
                "action": fields[0] if len(fields) > 0 else "",
                "sketch_file": fields[1] if len(fields) > 1 else "",
                "current_stage": fields[2] if len(fields) > 2 else "",
                "current_action": fields[3] if len(fields) > 3 else "",
                "timestamp": fields[4] if len(fields) > 4 else "",
            }
        except Exception as e:
            logger.error(f"Error reading full state: {e}")
            return {"active": False, "error": str(e)}

    def purge(self) -> bool:
        """Purge all state data"""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
            logger.info("State data purged")
            return True
        except Exception as e:
            logger.error(f"Error purging state: {e}")
            return False

# CODE DUMP

