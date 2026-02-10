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
            'loggingActive' : False,
            'logExtractionActive' : False,
            'csvReplayActive' : False,
            'logExtractionPath' : "",
            'csvReplayPath' : ""
        }

    def set(self, logging_active: bool, log_extraction_active: bool, csv_replay_active: bool,
            log_extraction_path: str, csv_replay_path: str):
        self._set_values(keys=list(self.get_default().keys()),
                         values=[logging_active, log_extraction_active, csv_replay_active,
                                 log_extraction_path, csv_replay_path])

    def set_extract(self, log_extraction_folder_name: str):
        self.set(logging_active=True, log_extraction_active=True, csv_replay_active=False,
                 log_extraction_path=log_extraction_folder_name, csv_replay_path="")

    def set_replay(self, log_extraction_folder_name : str, csv_replay_folder_name: str):
        self.set(logging_active=True, log_extraction_active=True, csv_replay_active=False,
                 log_extraction_path=log_extraction_folder_name, csv_replay_path=csv_replay_folder_name)