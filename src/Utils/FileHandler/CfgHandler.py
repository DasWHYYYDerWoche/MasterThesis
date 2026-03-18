from __future__ import annotations
from abc import ABC
from typing import override
from re import compile as re_compile
from pathlib import Path

from .FileHandler import FileHandler

class CfgHandler(FileHandler, ABC):
    """
    Represents a simple config file. Each line of the file must have the following structure:

    var_name = var_data;

    where var_name is a string and var_data is one of int, bool or str
    """
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