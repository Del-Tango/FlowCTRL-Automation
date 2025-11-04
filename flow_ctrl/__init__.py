"""
Flow-CTRL Automation Framework
"""

__version__ = "2.0.0"
__author__ = "Alveare Solutions"
__description__ = "Procedure automation framework"

# Fix: Use relative imports for package structure
from .src.core.engine import FlowEngine
from .src.core.procedure import Procedure
from .src.core.stage import Stage
from .src.core.action import Action
from .src.cli.interface import FlowCLI

# Shortcut imports
from .src.utils.logger import ConsoleOutput
from .src.config.settings import DEFAULT_CONFIG

# Public API
__all__ = [
    'FlowEngine',
    'Procedure',
    'Stage',
    'Action',
    'FlowCLI',
    'ConsoleOutput',
    'DEFAULT_CONFIG'
]

def get_version():
    """Get the current version of Flow-CTRL"""
    return __version__
