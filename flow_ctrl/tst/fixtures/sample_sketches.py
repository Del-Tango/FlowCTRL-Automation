"""
Sample procedure sketches for testing
"""

SIMPLE_SKETCH = {
    "name": "Test Procedure",
    "stage_1": [
        {
            "name": "action_1",
            "cmd": "echo 'Hello World'",
            "time": "5s",
            "timeout": "10s",
        }
    ],
}

MULTI_STAGE_SKETCH = {
    "name": "Multi-Stage Test",
    "setup_stage": [
        {"name": "create_dir", "cmd": "mkdir -p /tmp/test_dir", "time": "5s"}
    ],
    "main_stage": [
        {
            "name": "list_files",
            "cmd": "ls -la /tmp/test_dir",
            "time": "5s",
            "setup-cmd": "echo 'Starting file listing'",
            "teardown-cmd": "echo 'File listing complete'",
        }
    ],
    "cleanup_stage": [
        {"name": "remove_dir", "cmd": "rm -rf /tmp/test_dir", "time": "5s"}
    ],
}

INVALID_SKETCH = {
    "stage_1": [
        {
            "name": "invalid_action",
            # Missing required 'cmd' field
            "time": "invalid_time_format",
        }
    ]
}
