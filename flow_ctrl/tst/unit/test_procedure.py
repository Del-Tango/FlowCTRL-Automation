"""
Unit tests for Procedure class
"""

import pytest
from unittest.mock import Mock, patch

from flow_ctrl.src.core.procedure import Procedure
from tests.fixtures.sample_sketches import MULTI_STAGE_SKETCH


class TestProcedure:
    """Test Procedure functionality"""

    def test_procedure_initialization(self, test_config):
        """Test procedure initialization"""
        procedure = Procedure(MULTI_STAGE_SKETCH, test_config)

        assert procedure.name == "Multi-Stage Test"
        assert len(procedure.stages) == 3
        assert procedure.stats.total_stages == 3
        assert procedure.stats.total_actions == 3

    def test_parse_stages(self, test_config):
        """Test stage parsing"""
        procedure_data = {
            "name": "Test Procedure",
            "stage_1": [{"name": "action_1", "cmd": "echo 'test1'"}],
            "stage_2": [{"name": "action_2", "cmd": "echo 'test2'"}]
        }

        procedure = Procedure(procedure_data, test_config)

        assert len(procedure.stages) == 2
        assert procedure.stages[0].name == "stage_1"
        assert procedure.stages[1].name == "stage_2"

    @patch('flow_ctrl.src.core.procedure.Stage')
    def test_execute_success(self, mock_stage_class, test_config):
        """Test successful procedure execution"""
        mock_stage = Mock()
        mock_stage.name = "test_stage"
        mock_stage.execute.return_value = True
        mock_stage_class.return_value = mock_stage

        procedure_data = {
            "name": "Test Procedure",
            "stage_1": [{"name": "action_1", "cmd": "echo 'test'"}]
        }

        procedure = Procedure(procedure_data, test_config)
        result = procedure.execute()

        assert result is True
        assert procedure.stats.completed_stages == 1
        assert procedure.stats.success_count == 1

    @patch('flow_ctrl.src.core.procedure.Stage')
    def test_execute_with_stage_failure(self, mock_stage_class, test_config):
        """Test procedure execution with stage failure"""
        mock_stage = Mock()
        mock_stage.name = "test_stage"
        mock_stage.execute.return_value = False
        mock_stage_class.return_value = mock_stage

        procedure_data = {
            "name": "Test Procedure",
            "stage_1": [{"name": "action_1", "cmd": "echo 'test'"}]
        }

        procedure = Procedure(procedure_data, test_config)
        result = procedure.execute()

        assert result is False
        assert procedure.stats.failure_count == 1

    def test_get_progress(self, test_config):
        """Test progress reporting"""
        procedure_data = {
            "name": "Test Procedure",
            "stage_1": [{"name": "action_1", "cmd": "echo 'test'"}]
        }

        procedure = Procedure(procedure_data, test_config)
        progress = procedure.get_progress()

        assert progress['name'] == "Test Procedure"
        assert progress['stats']['total_stages'] == 1
        assert progress['stats']['total_actions'] == 1
