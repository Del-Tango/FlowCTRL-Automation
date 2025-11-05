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
    state_file: str = ".flow-ctrl.state.tmp"
    report_file: str = ".flow-ctrl.report.tmp"
    log_file: str = "flow-ctrl.log"
    log_name: str = "FlowCTRL"
    silence: bool = False
    debug: bool = False
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    timestamp_format: str = "%H:%M:%S"


BASE_DIR = Path(__file__).parent.parent.parent
DEFAULT_CONFIG = FlowConfig(
    project_dir=str(BASE_DIR),  # FIX: Use absolute path
    log_dir="logs",
    conf_dir="conf",
    state_file=".flow-ctrl.state.tmp",
    report_file=".flow-ctrl.report.tmp",
    log_file="flow-ctrl.log",
    log_name="FlowCTRL",
    silence=False,
    debug=False,
)

# Time conversion multipliers
TIME_MULTIPLIERS = {"s": 1, "m": 60, "h": 3600, "d": 86400}

# CODE DUMP
