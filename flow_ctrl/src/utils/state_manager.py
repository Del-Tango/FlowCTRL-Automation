"""
State management for procedure execution
"""

import csv
import logging

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """Manages procedure execution state"""

    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self._ensure_state_file()

    def _ensure_state_file(self):
        """Ensure state file exists"""
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.touch()

    def set_state(self, active: bool, action: str) -> bool:
        """Set overall procedure state"""
        try:
            if not active:
                # Clear state file when deactivating
                self.state_file.write_text('')
                logger.debug("State cleared")
                return True

            # Create state record
            state_record = [
                action,                    # Current action
                '',                        # Sketch file
                '',                        # Current stage
                '',                        # Current action
                datetime.now().isoformat() # Timestamp
            ]

            self.state_file.write_text(','.join(state_record))
            logger.debug(f"State set to: {action}")
            return True

        except Exception as e:
            logger.error(f"Error setting state: {e}")
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

            fields = content.split(',')
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
            if not self.get_state():
                # Create new state record if none exists
                state_record = [''] * 5
            else:
                # Read existing state
                content = self.state_file.read_text().strip()
                state_record = content.split(',')
                # Ensure we have enough fields
                while len(state_record) < 5:
                    state_record.append('')

            # Update the field
            state_record[field_index] = value
            # Always update timestamp
            state_record[4] = datetime.now().isoformat()

            self.state_file.write_text(','.join(state_record))
            logger.debug(f"State updated - field {field_index}: {value}")
            return True

        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return False

    def get_full_state(self) -> Dict[str, Any]:
        """Get complete state information"""
        if not self.get_state():
            return {'active': False}

        try:
            content = self.state_file.read_text().strip()
            fields = content.split(',')

            return {
                'active': True,
                'action': fields[0] if len(fields) > 0 else '',
                'sketch_file': fields[1] if len(fields) > 1 else '',
                'current_stage': fields[2] if len(fields) > 2 else '',
                'current_action': fields[3] if len(fields) > 3 else '',
                'timestamp': fields[4] if len(fields) > 4 else ''
            }
        except Exception as e:
            logger.error(f"Error reading full state: {e}")
            return {'active': False, 'error': str(e)}

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
