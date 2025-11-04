"""
Unit tests for Stage class
"""

import pytest
from unittest.mock import Mock, patch

from flow_ctrl.src.core.stage import Stage
from tests.fixtures.sample_sketches import SIMPLE_SKETCH


class TestStage:
    """Test Stage functionality"""

    def test_stage_initialization(self, test_config):
        """Test stage initialization"""
        stage_name = "test_stage"
        actions_data = SIMPLE_SKETCH["stage_1"]

        stage = Stage(stage_name, actions_data, test_config)

        assert stage.name == "test_stage"
        assert len(stage.actions) == 1
        assert stage.stats.total_actions == 1

    def test_parse_actions(self, test_config):
        """Test action parsing"""
        stage_name = "test_stage"
        actions_data = [
            {"name": "action_1", "cmd": "echo 'action1'"},
            {"name": "action_2", "cmd": "echo 'action2'"}
        ]

        stage = Stage(stage_name, actions_data, test_config)

        assert len(stage.actions) == 2
        assert stage.actions[0].name == "action_1"
        assert stage.actions[1].name == "action_2"

    @patch('flow_ctrl.src.core.stage.Action')
    def test_execute_success(self, mock_action_class, test_config):
        """Test successful stage execution"""
        mock_action = Mock()
        mock_action.name = "test_action"
        mock_action.execute.return_value = True
        mock_action.fatal_nok = False
        mock_action_class.return_value = mock_action

        stage_name = "test_stage"
        actions_data = [{"name": "action_1", "cmd": "echo 'test'"}]

        stage = Stage(stage_name, actions_data, test_config)
        result = stage.execute()

        assert result is True
        assert stage.stats.success_count == 1
        assert stage.stats.completed_actions == 1

    @patch('flow_ctrl.src.core.stage.Action')
    def test_execute_with_failure(self, mock_action_class, test_config):
        """Test stage execution with action failure"""
        mock_action = Mock()
        mock_action.name = "test_action"
        mock_action.execute.return_value = False
        mock_action.fatal_nok = False
        mock_action_class.return_value = mock_action

        stage_name = "test_stage"
        actions_data = [{"name": "action_1", "cmd": "echo 'test'"}]

        stage = Stage(stage_name, actions_data, test_config)
        result = stage.execute()

        assert result is False
        assert stage.stats.failure_count == 1

    def test_get_progress(self, test_config):
        """Test progress reporting"""
        stage_name = "test_stage"
        actions_data = [{"name": "action_1", "cmd": "echo 'test'"}]

        stage = Stage(stage_name, actions_data, test_config)
        progress = stage.get_progress()

        assert progress['name'] == "test_stage"
        assert progress['stats']['total_actions'] == 1
        assert progress['stats']['completed_actions'] == 0
