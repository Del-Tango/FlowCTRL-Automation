"""
Flow-CTRL Configuration
"""

import os
import json
import yaml

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class FlowConfig:
    """Main configuration class"""

    project_dir: str
    log_dir: str = "/tmp/flow_ctrl"
    conf_dir: str = "conf"
    state_file: str = ".flow-ctrl.state.tmp"
    report_file: str = ".flow-ctrl.report.tmp"
    log_file: str = "flow-ctrl.log"
    log_name: str = "FlowCTRL"
    silence: bool = False
    debug: bool = False
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    timestamp_format: str = "%H:%M:%S"

    @classmethod
    def from_file(
        cls, config_file: str, base_config: "FlowConfig" = None
    ) -> "FlowConfig":
        """
        Create configuration from JSON or YAML file

        Args:
            config_file: Path to configuration file
            base_config: Base configuration to use as defaults

        Returns:
            FlowConfig instance
        """
        if base_config is None:
            base_config = DEFAULT_CONFIG

        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")

            with open(config_path, "r") as f:
                if config_path.suffix.lower() in [".yaml", ".yml"]:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)

            # Use base_config values as defaults
            return cls(
                project_dir=config_data.get("project_dir", base_config.project_dir),
                log_dir=config_data.get("log_dir", base_config.log_dir),
                conf_dir=config_data.get("conf_dir", base_config.conf_dir),
                state_file=config_data.get("state_file", base_config.state_file),
                report_file=config_data.get("report_file", base_config.report_file),
                log_file=config_data.get("log_file", base_config.log_file),
                log_name=config_data.get("log_name", base_config.log_name),
                silence=config_data.get("silence", base_config.silence),
                debug=config_data.get("debug", base_config.debug),
                log_format=config_data.get("log_format", base_config.log_format),
                timestamp_format=config_data.get(
                    "timestamp_format", base_config.timestamp_format
                ),
            )

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration file: {e}")


BASE_DIR = Path(__file__).parent.parent.parent
DEFAULT_CONFIG = FlowConfig(
    project_dir=str(BASE_DIR),
    log_dir="/tmp/flow_ctrl",
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
