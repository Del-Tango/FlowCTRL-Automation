import logging
import os
import pysnooper

from .abstract_handler import Handler
from .stage_handler import StageHandler as Stage
from .backpack.bp_shell import shell_cmd as shell
from .backpack.bp_general import write2file, clear_screen, stdout_msg
from .validator import Validator

log = logging.getLogger(__name__)


class ProcedureHandler(Handler):
    '''
    [ NOTE ]: Interprets the content of a JSON procedure sketch file.
    '''

    def __init__(self, *args, **kwargs):
        self.state_file = kwargs.get('state_file', '/tmp/.flow-ctrl.state.tmp')
        self.report_file = kwargs.get('report_file', '/tmp/.flow-ctrl.report.tmp')
        self.stage_handler = kwargs.get(
            'stage_handler',
            Stage(report_file=self.report_file, state_file=self.state_file)
        )
        self.instruction_set = kwargs.get('sketch_file', str())

    def __print__(self, *args, **kwargs):
        return "Procedure Handler Instruction: {}, State: {}, Stage Handler: {}".format(
            self.instruction_set, self.state_flag, self.stage_handler
        )

    # FETCHERS

    def fetch_instruction(self):
        log.debug('')
        return self.instruction_set or []

    # PROCESSORS

#   @pysnooper.snoop()
    def process_sketch_stages(self, stages_dict):
        log.debug('')
        failures = 0
        for stage_id in stages_dict:
            if not self.stage_handler.set_instruction({stage_id: stages_dict[stage_id]}):
                failures += 1
                stdout_msg(
                    'Could not load procedure stage ({}) to handler! '
                    'Skipping ({})'.format(stage_id, stages_dict[stage_id]),
                    warn=True
                )
                continue
            stage = self.stage_handler.start()
            if not stage and stage == False:
                failures += 1
            elif not stage and stage == None:
                return
        if failures:
            stdout_msg(
                'Failures detected when processing ({}) sketch stages! ({})'
                .format(len(stages_dict.keys()), failures), warn=True
            )
        return False if failures else True

    # ACTIONS

    # TODO
    def stop(self):
        log.debug('WARNING: Under construction, building...')
        # Check state running and previous action in (start, resume)
        # if running, remove action anchor file - this instructs action handler to
        # stop
        if not self.validator.check_state(
                self.fetch_state(), self.fetch_state('action'), 'stop'):
            stdout_msg('Invalid state for action stop!', warn=True)
            stdout_msg('To force action execute with --purge beforehand.', info=True)
            return False
        self.set_state(True, 'stopped')
    def cont(self):
        log.debug('WARNING: Under construction, building...')
        # Check state not running and previous action paused
        # If paused check sketch file path
        # If sketch path valid fetch stage
        # If stage valid fetch action
        # Execute procedure handler - instruct to jump to stage/action
        if not self.validator.check_state(
                self.fetch_state(), self.fetch_state('action'), 'resume'):
            stdout_msg('Invalid state for action resume!', warn=True)
            stdout_msg('To force action execute with --purge beforehand.', info=True)
            return False
        self.set_state(True, 'resumed')

    def pause(self):
        log.debug('')
        if not self.validator.check_state(
                self.fetch_state(), self.fetch_state('action'), 'pause'):
            stdout_msg('Invalid state for action pause!', warn=True)
            stdout_msg('To force action execute with --purge beforehand.', info=True)
            return False
        failures, state = 0, self.set_state(True, 'paused')
        if not state:
            failures += 1
        pause = self.stage_handler.pause()
        if not pause:
            failures += 1
        if failures:
            stdout_msg(
                'Failures detected when processing ({}) sketch stages! ({})'
                .format(len(stages_dict.keys()), failures), warn=True
            )
        return False if failures else True

#   @pysnooper.snoop()
    def start(self):
        log.debug('')
        if not self.validator.check_state(
                self.fetch_state(), self.fetch_state('action'), 'start'):
            stdout_msg('Invalid state for action start!', warn=True)
            stdout_msg('To force action execute with --purge beforehand.', info=True)
            return False
        self.set_state(True, 'started')
        process = self.process_sketch_stages(self.fetch_instruction())
        return False if not process else True


    def purge(self):
        log.debug('')
        failures, stage_purge = 0, self.stage_handler.purge()
        if not stage_purge:
            stdout_msg('Stage handler could not be purged!', warn=True)
            failures += 1
        files_to_clean = [
            str(file_path) for file_path in (self.state_file, self.report_file)
            if file_path
        ]
        if not files_to_clean:
            failures += 1
        else:
            cleanup = shell('rm {}'.format(' '.join(files_to_clean)))
            if not cleanup:
                failures += 1
                stdout_msg(
                    'Could not cleanup files! ({})'.format(files_to_clean),
                    nok=True
                )
            else:
                stdout_msg('Purged all handler files!', ok=True)
        return False if failures else True

    def setup(self, *args, **kwargs):
        log.debug('')
        create_tmp_files = shell(
            'touch {} {} &> /dev/null'.format(self.state_file, self.report_file)
        )
        return create_tmp_files

# CODE DUMP


