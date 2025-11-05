"""
Validation logic for procedures, stages, and actions
"""

import logging

from pathlib import Path
from typing import Dict, Any, Union, List

logger = logging.getLogger(__name__)


class Validator:
    """Validates procedures, states, and configurations"""

    def validate_instruction(self, instruction: Union[Dict, List]) -> bool:
        """Validate instruction set"""
        if isinstance(instruction, list):
            # List of sketch file paths
            return all(
                Path(path).exists() for path in instruction if isinstance(path, str)
            )
        elif isinstance(instruction, dict):
            # Stage or action dictionary
            return bool(instruction)
        else:
            logger.error(f"Invalid instruction type: {type(instruction)}")
            return False

    def validate_state(self, state: bool, previous_action: str, action: str) -> bool:
        """Validate state transition"""
        state_validators = {
            "start": self._validate_start,
            "stop": self._validate_stop,
            "pause": self._validate_pause,
            "resume": self._validate_resume,
        }

        if action not in state_validators:
            logger.error(f"Invalid action: {action}")
            return False

        return state_validators[action](state, previous_action, action)

    def _validate_start(self, state: bool, previous_action: str, action: str) -> bool:
        """Validate start action state"""
        if not state and not previous_action:
            return True
        return previous_action in ("purged", "")

    def _validate_stop(self, state: bool, previous_action: str, action: str) -> bool:
        """Validate stop action state"""
        return previous_action in ("started", "resumed")

    def _validate_pause(self, state: bool, previous_action: str, action: str) -> bool:
        """Validate pause action state"""
        return self._validate_stop(state, previous_action, action)

    def _validate_resume(self, state: bool, previous_action: str, action: str) -> bool:
        """Validate resume action state"""
        return previous_action == "paused"

    def validate_action_config(self, action_data: Dict[str, Any]) -> bool:
        """Validate action configuration"""
        required_fields = ["name", "cmd"]

        for field in required_fields:
            if field not in action_data:
                logger.error(f"Action missing required field: {field}")
                return False

        # Validate time formats if present
        time_fields = ["time", "timeout"]
        for field in time_fields:
            if field in action_data:
                if not self._validate_time_format(action_data[field]):
                    logger.error(
                        f"Invalid time format in {field}: {action_data[field]}"
                    )
                    return False

        return True

    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format string"""
        if not time_str:
            return True

        try:
            unit = time_str[-1].lower()
            value = int(time_str[:-1])

            valid_units = ["s", "m", "h", "d"]
            return unit in valid_units and value > 0
        except (ValueError, IndexError):
            return False

    def validate_sketch_file(self, file_path: str) -> bool:
        """Validate procedure sketch file"""
        path = Path(file_path)

        if not path.exists():
            logger.error(f"Sketch file not found: {file_path}")
            return False

        if path.suffix.lower() != ".json":
            logger.error(f"Sketch file must be JSON: {file_path}")
            return False

        try:
            import json

            with open(path, "r") as f:
                data = json.load(f)

            # Basic structure validation
            if not isinstance(data, dict):
                logger.error("Sketch file must contain a JSON object")
                return False

            # Validate stages
            for stage_name, actions in data.items():
                if stage_name == "name":
                    continue

                if not isinstance(actions, list):
                    logger.error(f"Stage {stage_name} must contain a list of actions")
                    return False

                for action in actions:
                    if not self.validate_action_config(action):
                        return False

            return True

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in sketch file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating sketch file: {e}")
            return False

# CODE DUMP
