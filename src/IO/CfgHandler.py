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
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key,raw_value = line.split("=")
                key = key.strip()
                raw_value = raw_value.strip().rstrip(";")
                if raw_value.lower() == "true":
                    value = True
                elif raw_value.lower() == "false":
                    value = False
                elif raw_value.startswith('"') and raw_value.endswith('"'):
                    value = raw_value[1:-1]  # remove quotes
                elif raw_value.startswith('[') and raw_value.endswith(']'):
                    raw_value = raw_value[1:-1] #remove brackets
                    value = [element for element in raw_value.split(',')]
                    try:
                        value = [int(element) for element in value]
                    except ValueError:
                        pass
                else:
                    try:
                        value = int(raw_value)
                    except ValueError:
                        value = raw_value
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
                val_str = value
            elif isinstance(value, list):
                val_str = "["
                for element in value:
                    val_str += str(element)
                    val_str += ","
                if len(val_str) > 1:
                    val_str = val_str[0:-1]
                val_str += "]"
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