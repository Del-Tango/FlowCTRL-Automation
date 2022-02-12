import json
import logging
import os

# CONVERTORS


def json2dict(file_path):
    if not file_path or not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as fl:
        return json.load(fl)
