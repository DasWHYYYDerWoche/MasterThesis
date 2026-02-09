from __future__ import annotations
from abc import ABC
from typing import override, Optional
from re import compile as re_compile
from pathlib import Path

from .FileHandler import  FileHandler
from ...Utils import PATH_CONFIG

class CfgHandler(FileHandler, ABC):
    def __init__(self, path: Path):
        super().__init__(path)

    @override
    def _load_from_file(self):
        f = None
        try:
            f = open(self._path, "r")
            text = f.read()
            pattern = re_compile(r'(\w+)\s*=\s*(.+?);')
            for key, raw_value in pattern.findall(text):
                value = raw_value.strip()
                # Convert value to appropriate Python type
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]  # remove quotes
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        # leave value as string
                        pass
                self._data[key] = value
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

    @override
    def _write_to_file(self):
        text = ""
        for key, value in self._data.items():
            if isinstance(value, bool):
                val_str = "true" if value else "false"
            elif isinstance(value, str):
                val_str = f'"{value}"'
            else:
                val_str = str(value)
            text += f"{key} = {val_str};\n"
        f = None
        try:
            f = open(self._path, "w")
            f.write(text)
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

class LoggerHandler(CfgHandler):
    def __init__(self):
        super().__init__(PATH_CONFIG / "loggerT.cfg")

    @override
    def get_default(self) -> dict:
        return {
            'logging': False,
            'logExtraction': False,
            'csvReplay': False,
            'actionName': '',
            'parameterSet': '',
            'recordingDate': '',
            'logIndex': -1,
            'csvName': ''
        }

    def set(self, logging: bool, log_extraction: bool, csv_replay: bool, action_name: str, parameter_set : str, recording_date: str, log_index: int, csv_name: str):
        self._set_values(keys=['logging', 'logExtraction', 'csvReplay', 'actionName', 'parameterSet', 'recordingDate', 'logIndex', 'csvName'],
                         values=[logging, log_extraction, csv_replay, action_name, parameter_set, recording_date, log_index, csv_name])

    def set_extract(self, action_name: str, recording_date: str, log_index: int):
        self.set(logging=True, log_extraction=True, csv_replay=False, action_name=action_name, parameter_set="",
                             recording_date=recording_date, log_index=log_index, csv_name="")

    def set_replay(self, action_name: str, parameter_set: str, recording_date: str, log_index: int, csv_name: str):
        self.set(logging=True, log_extraction=False, csv_replay=True, action_name=action_name, parameter_set=parameter_set,
                             recording_date=recording_date, log_index=log_index, csv_name=csv_name)