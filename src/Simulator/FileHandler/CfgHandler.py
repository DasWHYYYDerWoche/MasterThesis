from __future__ import annotations
from abc import ABC
from typing import override
from re import compile as re_compile
from pathlib import Path

from .FileHandler import  FileHandler
from ..Simulator import PATH_LOGGER_CFG

class CfgHandler(FileHandler, ABC):
    def __init__(self, path: Path):
        super().__init__(path)

    @override
    def _load(self):
        with open(self._path, "r") as f:
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
                        pass  # leave as string if not int

                self._data[key] = value

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
        with open(PATH_LOGGER_CFG, "w") as f:
            f.write(text)



class LoggerHandler(CfgHandler):
    def __init__(self):
        super().__init__(PATH_LOGGER_CFG)

    @override
    def get_default(self) -> dict:
        return {
            'logging': False,
            'logExtraction': False,
            'csvReplay': False,
            'actionName': '',
            'logFolder': '',
            'logIndex': -1,
            'csvName': ''
        }

    def set(self, logging: bool, log_extraction: bool, csv_replay: bool, action_name: str, log_folder: str, log_index: int, csv_name: str):
        self.set_values(keys=self.keys, values=[logging, log_extraction, csv_replay, action_name, log_folder, log_index, csv_name ])

    def set_extract(self, action_name: str, log_folder: str, log_index: int, csv_name: str):
        self.set(logging=True, log_extraction=True, csv_replay=False, action_name=action_name,
                             log_folder=log_folder, log_index=log_index, csv_name=csv_name)

    def set_replay(self, action_name: str, log_folder: str, log_index: int, csv_name: str):
        self.set(logging=True, log_extraction=False, csv_replay=True, action_name=action_name,
                             log_folder=log_folder, log_index=log_index, csv_name=csv_name)