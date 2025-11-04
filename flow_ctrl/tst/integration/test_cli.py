"""
Integration tests for CLI interface
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from flow_ctrl.src.cli.interface import FlowCLI, main
from flow_ctrl.tst.fixtures.sample_sketches import SIMPLE_SKETCH


class TestFlowCLI:
    """Integration tests for FlowCLI"""

    def test_cli_help(self):
        """Test CLI help command"""
        cli = FlowCLI()

        with patch('sys.argv', ['flow-ctrl', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                cli.parse_arguments()
            assert exc_info.value.code == 0

    def test_cli_version_check(self):
        """Test version import and check"""
        import flow_ctrl
        assert flow_ctrl.__version__ == "2.0.0"
        assert flow_ctrl.get_version() == "2.0.0"

    @patch('flow_ctrl.src.cli.interface.FlowEngine')
    def test_cli_purge_command(self, mock_engine_class, capsys):
        """Test CLI purge command"""
        mock_engine = Mock()
        mock_engine.purge_data.return_value = Mock(exit_code=0)
        mock_engine_class.return_value = mock_engine

        with patch('sys.argv', ['flow-ctrl', '--purge', '--silence']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    @patch('flow_ctrl.src.cli.interface.FlowEngine')
    def test_cli_start_without_sketch(self, mock_engine_class, capsys):
        """Test CLI start command without sketch file"""
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine

        with patch('sys.argv', ['flow-ctrl', '--start', '--silence']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_cli_argument_parsing(self):
        """Test CLI argument parsing"""
        cli = FlowCLI()

        test_args = ['flow-ctrl', '--start', '--sketch-file', 'test.json', '--debug']
        with patch('sys.argv', test_args):
            args = cli.parse_arguments()

            assert args.start is True
            assert args.sketch_file == 'test.json'
            assert args.debug is True
            assert args.silence is False
