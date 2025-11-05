"""
Stage representation and execution logic
"""

import logging

from typing import Dict, List, Any
from dataclasses import dataclass

from .action import Action
from ..utils.state_manager import StateManager

logger = logging.getLogger(__name__)


@dataclass
class StageStats:
    """Stage execution statistics"""

    total_actions: int
    completed_actions: int
    success_count: int
    failure_count: int


class Stage:
    """Represents a stage within a procedure"""

    def __init__(self, name: str, actions_data: List[Dict[str, Any]], config):
        self.name = name
        self.config = config
        self.actions: List[Action] = []

        # FIX: Remove non-existent handler
        # self.handler = StageHandler(config)
        self.state_manager = StateManager(config.state_file)
        self.stats = StageStats(0, 0, 0, 0)

        self._parse_actions(actions_data)

    def _parse_actions(self, actions_data: List[Dict[str, Any]]):
        """Parse actions from stage data"""
        for action_data in actions_data:
            action = Action(action_data, self.config)
            self.actions.append(action)
            self.stats.total_actions += 1

    def execute(self) -> bool:
        """Execute all actions in the stage"""
        logger.info(f"Executing stage: {self.name}")

        try:
            for action in self.actions:
                self.state_manager.update_state(3, action.name)  # Record current action

                logger.info(f"Processing action: {action.name}")
                action_success = action.execute()

                if action_success:
                    self.stats.completed_actions += 1
                    self.stats.success_count += 1
                else:
                    self.stats.failure_count += 1
                    # Check if we should continue on action failure
                    if not self._should_continue_on_failure(action):
                        logger.error(f"Action failed, terminating stage: {action.name}")
                        return False

            success = self.stats.failure_count == 0
            logger.info(f"Stage completed: {'SUCCESS' if success else 'FAILED'}")
            return success

        except Exception as e:
            logger.error(f"Stage execution error: {e}")
            return False

    def _should_continue_on_failure(self, action: "Action") -> bool:
        """Determine if stage should continue after action failure"""
        # Check if action is marked as fatal
        return not action.fatal_nok

    def get_progress(self) -> Dict[str, Any]:
        """Get current stage progress"""
        return {
            "name": self.name,
            "current_action": self.state_manager.get_state_field(3)
            if self.state_manager.get_state()
            else None,
            "stats": {
                "total_actions": self.stats.total_actions,
                "completed_actions": self.stats.completed_actions,
                "success_count": self.stats.success_count,
                "failure_count": self.stats.failure_count,
            },
        }
