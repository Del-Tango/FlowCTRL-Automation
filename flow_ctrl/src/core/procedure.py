"""
Procedure representation and execution logic
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .stage import Stage

# FIX: Remove non-existent handler imports
# from handlers.procedure_handler import ProcedureHandler
from ..utils.state_manager import StateManager  # FIX: Correct import path

logger = logging.getLogger(__name__)

@dataclass
class ProcedureStats:
    """Procedure execution statistics"""
    total_stages: int
    completed_stages: int
    total_actions: int
    completed_actions: int
    success_count: int
    failure_count: int

class Procedure:
    """Represents a complete automation procedure"""

    def __init__(self, data: Dict[str, Any], config):
        self.data = data
        self.config = config
        self.name = data.get('name', 'Unnamed Procedure')
        self.stages: List[Stage] = []
        # FIX: Remove non-existent handler
        # self.handler = ProcedureHandler(config)
        self.state_manager = StateManager(config.state_file)
        self.stats = ProcedureStats(0, 0, 0, 0, 0, 0)

        self._parse_stages()

    def _parse_stages(self):
        """Parse stages from procedure data"""
        for stage_name, actions_data in self.data.items():
            if stage_name == 'name':
                continue

            stage = Stage(stage_name, actions_data, self.config)
            self.stages.append(stage)
            self.stats.total_stages += 1
            self.stats.total_actions += len(actions_data)

    def execute(self) -> bool:
        """Execute the complete procedure"""
        logger.info(f"Executing procedure: {self.name}")

        try:
            for stage in self.stages:
                self.state_manager.update_state(2, stage.name)  # Record current stage

                logger.info(f"Processing stage: {stage.name}")
                stage_success = stage.execute()

                if stage_success:
                    self.stats.completed_stages += 1
                    self.stats.success_count += 1
                else:
                    self.stats.failure_count += 1
                    # Check if we should continue on failure
                    if not self._should_continue_on_failure():
                        logger.error(f"Stage failed, terminating procedure: {stage.name}")
                        return False

            # Final cleanup
            self._cleanup()

            success = self.stats.failure_count == 0
            logger.info(f"Procedure completed: {'SUCCESS' if success else 'FAILED'}")
            return success

        except Exception as e:
            logger.error(f"Procedure execution error: {e}")
            return False

    def _should_continue_on_failure(self) -> bool:
        """Determine if procedure should continue after failure"""
        # Implementation would check procedure-level configuration
        return True

    def _cleanup(self):
        """Cleanup after procedure execution"""
        # Implementation would handle post-execution cleanup
        pass

    def get_progress(self) -> Dict[str, Any]:
        """Get current execution progress"""
        return {
            'name': self.name,
            'current_stage': self.state_manager.get_state_field(2) if self.state_manager.get_state() else None,
            'stats': {
                'total_stages': self.stats.total_stages,
                'completed_stages': self.stats.completed_stages,
                'total_actions': self.stats.total_actions,
                'completed_actions': self.stats.completed_actions,
                'success_count': self.stats.success_count,
                'failure_count': self.stats.failure_count
            }
        }
