# FlowCTRL-Automation

## Overview

FlowCTRL is a robust procedure automation framework designed to execute complex workflows defined in JSON sketch files. It provides a structured approach to automating multi-stage procedures with comprehensive error handling, state management, and real-time monitoring capabilities.

### Features

- Multi-stage Procedure Execution: Define complex workflows with multiple stages and actions
- State Management: Persistent state tracking with pause/resume functionality
- Comprehensive Error Handling: Setup, teardown, success, and failure command hooks
- Timeout Control: Configurable timeouts for each action
- Real-time Monitoring: Live progress tracking and logging
- CLI Interface: Easy-to-use command-line interface
- Extensible Architecture: Modular design for easy customization

### Quick Start

#### Installation
```bash
git clone <repository-url>
cd FlowCTRL-Automation
```

#### Basic Usage
```bash
# Start a procedure
./flow-init --start --sketch-file dump/test_procedure.json

# Pause a running procedure
./flow-init --pause

# Resume a paused procedure
./flow-init --resume

# Stop a procedure
./flow-init --stop

# Purge all state and logs
./flow-init --purge
```

#### Procedure Sketch Format

Define your automation procedures using JSON sketch files:
```json
{
    "Stage_ID": [
        {
            "name": "Action_ID",
            "time": "5m",
            "timeout": "10m",
            "cmd": "ls -la && echo 'Operation completed'",
            "setup-cmd": "echo 'Preparing execution...'",
            "teardown-cmd": "echo 'Cleaning up...'",
            "on-ok-cmd": "echo 'Success handler'",
            "on-nok-cmd": "echo 'Error handler'",
            "fatal-nok": false
        }
    ]
}
```

#### Field Definitions

- name: Unique identifier for the action
- time: Estimated execution time (e.g., "5m", "1h", "2d")
- timeout: Maximum allowed execution time
- cmd: Main command to execute
- setup-cmd: Command run before main execution
- teardown-cmd: Command run after main execution
- on-ok-cmd: Command run if main command succeeds
- on-nok-cmd: Command run if main command fails
- fatal-nok: Whether to terminate session on failure

## Architecture

### Core Components
```text
src/
├── abstract_handler.py    # Base handler class
├── action_handler.py      # Individual action execution
├── stage_handler.py       # Stage-level processing
├── procedure_handler.py   # Top-level procedure management
└── validator.py           # Input validation
```

### Handler Hierarchy

- ProcedureHandler: Manages entire procedure execution
- StageHandler: Processes individual stages
- ActionHandler: Executes specific actions within stages

## Testing

### Unit Tests
```bash
# Run all unit tests
python -m pytest test/unit-tests/

# Run specific test modules
python -m pytest test/unit-tests/test_action_handler.py
python -m pytest test/unit-tests/test_stage_handler.py
python -m pytest test/unit-tests/test_procedure_handler.py
python -m pytest test/unit-tests/test_validator.py
```

### Functional Tests
```bash
# Test CLI execution
python -m pytest test/functional-tests/test_cli_execution.py
```

## Configuration

Default configuration is stored in conf/flow-ctrl.conf.json:
```json
{
    "state-file": "/tmp/.flow-ctrl.state.tmp",
    "report-file": "/tmp/.flow-ctrl.report.tmp",
    "log-file": "flow-ctrl.log",
    "log-dir": "log",
    "log-name": "FlowCTRL",
    "silence": false,
    "debug": false
}
```

## API Reference

### Core Methods

- start(): Begin procedure execution
- stop(): Gracefully stop procedure
- pause(): Pause current execution
- cont(): Resume paused procedure
- purge(): Cleanup all state files
- load(sketch_file): Load procedure definition

### State Management

The framework maintains state in /tmp/.flow-ctrl.state.tmp with format:
action_label,sketch_file,current_stage,current_action,timestamp

#### Examples

Simple Procedure
```json
{
    "System_Check": [
        {
            "name": "Disk_Space",
            "time": "1m",
            "cmd": "df -h",
            "timeout": "2m",
            "on-ok-cmd": "echo 'Disk space check passed'",
            "on-nok-cmd": "echo 'Disk space issues detected'"
        }
    ]
}
```

Complex Multi-stage Workflow
```json
{
    "Preparation": [
        {
            "name": "Backup_Data",
            "time": "10m",
            "cmd": "tar -czf backup.tar.gz /important/data",
            "timeout": "15m",
            "fatal-nok": true
        }
    ],
    "Deployment": [
        {
            "name": "Update_System",
            "time": "5m",
            "cmd": "apt update && apt upgrade -y",
            "timeout": "10m"
        }
    ]
}
```

Regards, the Alveare Solutions #!/Society -x
