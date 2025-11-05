"""
Command-line interface for Flow-CTRL
"""

import argparse
import sys
import pysnooper

from pathlib import Path
from typing import Optional

from ..core.engine import FlowEngine
from ..config.settings import DEFAULT_CONFIG
from ..utils.logger import ConsoleOutput


class FlowCLI:
    """Command-line interface for Flow-CTRL"""

    def __init__(self):
        self.engine: Optional[FlowEngine] = None
        self.config = DEFAULT_CONFIG

    def parse_arguments(self):
        """Parse command line arguments"""

        if not self.config.silence:
            self._display_banner()

        parser = argparse.ArgumentParser(
            usage="""flow_ctrl [-h] [-f FILE] [-c FILE] [-l FILE] [-S|-s|-p|-R] [-P] [--silence] [--debug]

[ EXAMPLE ]:

    ~$ flow_ctrl --start --sketch-file automate_me.json
    ~$ flow_ctrl --purge --start --sketch-file automate_me.json
    ~$ flow_ctrl --pause
    ~$ flow_ctrl --resume
    ~$ flow_ctrl --stop

[ EXAMPLE ]: Procedure sketch JSON format:

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
}"""
        )

        parser.add_argument(
            "--sketch-file",
            "-f",
            type=str,
            help="Path to JSON sketch file containing procedure",
        )
        parser.add_argument(
            "--config-file", "-c", type=str, help="Path to configuration file"
        )
        parser.add_argument("--log-file", "-l", type=str, help="Path to log file")

        # Action arguments
        action_group = parser.add_argument_group("Actions")
        action_group.add_argument(
            "--start", "-S", action="store_true", help="Start automation process"
        )
        action_group.add_argument(
            "--stop", "-s", action="store_true", help="Stop currently running process"
        )
        action_group.add_argument(
            "--pause", "-p", action="store_true", help="Pause currently running process"
        )
        action_group.add_argument(
            "--resume", "-R", action="store_true", help="Resume paused process"
        )
        action_group.add_argument(
            "--purge",
            "-P",
            action="store_true",
            help="Purge all data and cleanup files",
        )

        # Other options
        parser.add_argument(
            "--silence",
            action="store_true",
            help="Suppress banner and non-essential output",
        )
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")

        return parser.parse_args()

    def setup_engine(self, args):
        """Setup the flow engine with configuration"""
        # Update config based on arguments
        if args.config_file:
            self.config.conf_dir = str(Path(args.config_file).parent)

        if args.log_file:
            self.config.log_file = args.log_file

        if args.silence:
            self.config.silence = True

        if args.debug:
            self.config.debug = True

        # Create engine
        self.engine = FlowEngine(self.config)

    def send_external_command(self, command: str) -> bool:
        """Send a command to a running Flow-CTRL process"""
        if not self.engine:
            ConsoleOutput.error("Engine not initialized")
            return False

        return self.engine.send_external_command(command)

    def run_external_control(self, args):
        """Run in external control mode"""
        if args.pause:
            ConsoleOutput.info("Sending PAUSE command to running process...")
            return self.send_external_command("pause")
        elif args.resume:
            ConsoleOutput.info("Sending RESUME command to running process...")
            return self.send_external_command("resume")
        elif args.stop:
            ConsoleOutput.info("Sending STOP command to running process...")
            return self.send_external_command("stop")
        else:
            ConsoleOutput.error("No external command specified")
            return False

    def run(self):
        """Run the CLI"""
        args = self.parse_arguments()

        # Check if this is an external control command
        if any([args.pause, args.resume, args.stop]) and not args.start:
            # External control mode - don't start engine fully, just send command
            self.setup_engine(args)
            success = self.run_external_control(args)
            sys.exit(0 if success else 1)

        # Normal execution mode
        self.setup_engine(args)

        # Execute requested actions
        exit_code = 0

        try:
            if args.purge:
                result = self.engine.purge_data()
                ConsoleOutput.info(result)
                exit_code = result.exit_code

            if args.start:
                if not args.sketch_file:
                    ConsoleOutput.error("Sketch file required for start action")
                    exit_code = 1
                else:
                    if self.engine.load_procedure(args.sketch_file):
                        result = self.engine.start_procedure()
                        ConsoleOutput.info(result)
                        exit_code = result.exit_code
                    else:
                        ConsoleOutput.error("Failed to load procedure")
                        exit_code = 1

            elif args.stop:
                result = self.engine.stop_procedure()
                ConsoleOutput.info(result)
                exit_code = result.exit_code

            elif args.pause:
                result = self.engine.pause_procedure()
                ConsoleOutput.info(result)
                exit_code = result.exit_code

            elif args.resume:
                result = self.engine.resume_procedure()
                ConsoleOutput.info(result)
                exit_code = result.exit_code

            else:
                # No action specified, show help
                if not args.silence:
                    ConsoleOutput.info(
                        "No action specified. Use --help for usage information."
                    )

        except KeyboardInterrupt:
            ConsoleOutput.info("Operation interrupted by user")
            exit_code = 130
        except Exception as e:
            ConsoleOutput.error(f"Unexpected error: {e}")
            exit_code = 1

        sys.exit(exit_code)

    def _cli_banner(self):
        banner = """
    ___________________________________________________________________________

      *              *   Flow CTRL * Automation Framework   *               *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x
        """
        return banner

    def _display_banner(self):
        """Display application banner"""
        banner = self._cli_banner()
        ConsoleOutput.banner(banner)


def main():
    """Main entry point"""
    cli = FlowCLI()
    cli.run()


if __name__ == "__main__":
    main()
