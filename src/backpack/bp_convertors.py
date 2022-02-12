import json
import logging
import os

log = logging.getLogger('FlowCTRL')

# CONVERTORS


def json2dict(file_path):
    if not file_path or not os.path.exists(file_path):
        log.warning('File not found! ({})'.format(file_path))
        return {}
    with open(file_path, 'r') as fl:
        converted = json.load(fl)
    log.debug('Converted JSON: ({})'.format(converted))
    return converted
