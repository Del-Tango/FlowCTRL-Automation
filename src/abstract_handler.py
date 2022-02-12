import logging
import os
import pysnooper

from abc import ABC
from .backpack.bp_convertors import json2dict
from .backpack.bp_general import write2file
from .backpack.bp_shell import shell_cmd as shell
from .validator import Validator

log = logging.getLogger(__name__)


class Handler(ABC):

    instruction_set = None
    state_flag = False
    state_file = str()
    validator = Validator()

    def __init__(self, *args, **kwargs):
        log.debug('')
        self.instruction_set = kwargs.get('instruction_set')

#   @abstractmethod
    def fetch_instruction(self):
        log.debug('')
        return self.instruction_set

#   @abstractmethod
#   @pysnooper.snoop()
    def set_instruction(self, instruction_set):
        log.debug('')
        if not self.validator.check_instruction(instruction_set):
            return False
        self.instruction_set = instruction_set
        return True

#   @classmethod
#   @pysnooper.snoop()
    def fetch_state(self, state='flag'):
        log.debug('')
        if not os.path.exists(self.state_file):
            return False if state != 'action' else str()
        content = []
        with open(self.state_file, 'r') as fl:
            content = [item.strip('\n') for item in fl.readlines()]
        if not len(content):
            return False if state != 'action' else str()
        return content[0].split(',')[0] if state == 'action' else True

#   @classmethod
#   @pysnooper.snoop()
    def set_state(self, state_flag, action_label):
        log.debug('')
        self.state_flag = False
        if not state_flag:
            shell('rm {}'.format(self.state_file))
            return True
        state_record = "{},{},{},{}".format(
            action_label,self.instruction_set,'',''
        )
        return write2file(state_record, file_path=self.state_file, mode='w')

#   @classmethod
#   @pysnooper.snoop()
    def load(self, json_file):
        log.debug('')
        converted = json2dict(json_file)
        if not json_file or not converted:
            return False
        self.set_instruction(json2dict(json_file))
        return self.instruction_set

#   @abstractmethod
    def start(self):
        pass

#   @abstractmethod
    def stop(self):
        pass

#   @abstractmethod
    def cont(selif):            # Continue
        pass

#   @abstractmethod
    def purge(self):
        pass

    def setup(self):
        pass

# CODE DUMP

