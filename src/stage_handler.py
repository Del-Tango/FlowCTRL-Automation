import logging

from .backpack.bp_shell import shell_cmd as shell
from .backpack.bp_general import write2file, stdout_msg
from .abstract_handler import Handler
from .action_handler import ActionHandler as Action


log = logging.getLogger(__name__)


class StageHandler(Handler):
    '''
    [ NOTE ]: StageHandler processes one procedure stage at a time as defined
              in the procedure sketch file.
    '''

    def __init__(self, *args, **kwargs):
        self.state_file = kwargs.get('state_file', '/tmp/.flow-ctrl.state.tmp')
        self.report_file = kwargs.get('report_file', '/tmp/.flow-ctrl.report.tmp')
        self.action_handler = kwargs.get(
            'action_handler',
            Action(report_file=self.report_file, state_file=self.state_file)
        )

    def __print__(self, *args, **kwargs):
        return 'Stage Handler Instruction: {}, Action Handler: {}'.format(
            self.instruction_set, self.action_handler
        )

    # PROCESSORS

    def process_stage_actions(self, actions_list):
        log.debug('')
        failures = 0
        for action_record_dict in actions_list:
            if not self.fetch_state() or self.fetch_state('action') \
                    not in ('started', 'resumed'):
                stdout_msg(
                    'Terminate signal received at action ({})'.format(
                    action_record_dict.get('name', 'Unknown')), warn=True
                )
                return False
            if not self.action_handler.set_instruction(action_record_dict):
                failures += 1
                stdout_msg(
                    'Could not load action record to handler! '
                    'Skipping ({})'.format(action_record_dict), warn=True
                )
                continue
            action = self.action_handler.start()
            if not action:
                failures += 1
        if failures:
            stdout_msg(
                'Failures detected when processing stage actions! ({})'
                .format(failures), warn=True
            )
        return False if failures else True

    # ACTIONS

    def start(self):
        log.debug('')
        failures, instruction = 0, self.fetch_instruction()
        if not self.validator.check_instruction(instruction):
            log.error(
                'Invalid instruction set for stage handler! ({})'
                .format(instruction)
            )
            return False
        for stage_label in instruction:
            if not self.fetch_state() or self.fetch_state('action') \
                    not in ('started', 'resumed'):
                stdout_msg(
                    'Terminate signal received at stage ({})'.format(stage_label),
                    warn=True
                )
                return
            stdout_msg(
                'Processing procedure stage... ({})'.format(stage_label),
                info=True
            )
            process = self.process_stage_actions(instruction.get(stage_label))
            if not process:
                failures += 1
                continue
            stdout_msg(
                'Procedure Stage! ({})\n...'.format(stage_label), done=True
            )
        if failures:
            stdout_msg(
                'Failures detected when processing stage! ({}, {})'
                .format(stage_label, failures), warn=True
            )
        return False if failures else True

    # TODO
    def stop(self):
        log.debug('WARNING: Under construction, building...')
    def cont(self):
        log.debug('WARNING: Under construction, building...')
    def purge(self):
        log.debug('WARNING: Under construction, building...')
    def pause(self):
        log.debug('WARNING: Under construction, building...')
