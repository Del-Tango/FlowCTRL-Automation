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

    # @pysnooper.snoop()
    def run(self):
        """Run the CLI"""

        args = self.parse_arguments()

        # Setup engine
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
