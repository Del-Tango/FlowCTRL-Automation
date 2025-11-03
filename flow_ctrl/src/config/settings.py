"""
Flow-CTRL Configuration
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class FlowConfig:
    """Main configuration class"""
    project_dir: str
    log_dir: str = "logs"
    conf_dir: str = "conf"
    state_file: str = "/tmp/.flow-ctrl.state.tmp"
    report_file: str = "/tmp/.flow-ctrl.report.tmp"
    log_file: str = "flow-ctrl.log"
    log_name: str = "FlowCTRL"
    silence: bool = False
    debug: bool = False
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    timestamp_format: str = '%H:%M:%S'

# FIX: Use proper path resolution
BASE_DIR = Path(__file__).parent.parent.parent
DEFAULT_CONFIG = FlowConfig(
    project_dir=str(BASE_DIR),  # FIX: Use absolute path
    log_dir="logs",
    conf_dir="conf",
    state_file="/tmp/.flow-ctrl.state.tmp",
    report_file="/tmp/.flow-ctrl.report.tmp",
    log_file="flow-ctrl.log",
    log_name="FlowCTRL",
    silence=False,
    debug=False
)

# Behavior codes
BEHAVIOR_CODES = {
    'continue': 100,
    'repeat': 101,
    'restart': 102,
    'game_over': 103,
    'continue_indexed': 104,
    'continue_unindexed': 105,
    'repeat_indexed': 106,
    'repeat_unindexed': 107
}

# Time conversion multipliers
TIME_MULTIPLIERS = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400
}

# CODE DUMP

#   """
#   Flow-CTRL Configuration
#   """

#   import os
#   from pathlib import Path
#   from typing import Dict, Any, List
#   from dataclasses import dataclass

#   @dataclass
#   class FlowConfig:
#       """Main configuration class"""
#       project_dir: str
#       log_dir: str = "logs"
#       conf_dir: str = "conf"
#       state_file: str = "/tmp/.flow-ctrl.state.tmp"
#       report_file: str = "/tmp/.flow-ctrl.report.tmp"
#       log_file: str = "flow-ctrl.log"
#       log_name: str = "FlowCTRL"
#       silence: bool = False
#       debug: bool = False
#       log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#       timestamp_format: str = '%H:%M:%S'

#   # Default settings
#   DEFAULT_CONFIG = FlowConfig(
#       project_dir=Path(__file__).parent.parent,
#       log_dir="logs",
#       conf_dir="conf",
#       state_file="/tmp/.flow-ctrl.state.tmp",
#       report_file="/tmp/.flow-ctrl.report.tmp",
#       log_file="flow-ctrl.log",
#       log_name="FlowCTRL",
#       silence=False,
#       debug=False
#   )

#   # Behavior codes
#   BEHAVIOR_CODES = {
#       'continue': 100,
#       'repeat': 101,
#       'restart': 102,
#       'game_over': 103,
#       'continue_indexed': 104,
#       'continue_unindexed': 105,
#       'repeat_indexed': 106,
#       'repeat_unindexed': 107
#   }

#   # Time conversion multipliers
#   TIME_MULTIPLIERS = {
#       's': 1,
#       'm': 60,
#       'h': 3600,
#       'd': 86400
#   }
