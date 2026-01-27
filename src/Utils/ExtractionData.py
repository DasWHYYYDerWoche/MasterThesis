from __future__ import annotations

class ExtractionData:
    def __init__(self, action_name : str, log_folder : str, log_index : int):
        self._action_name = action_name
        self._log_folder = log_folder
        self._log_index = log_index

    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def log_folder(self) -> str:
        return self._log_folder

    @property
    def log_index(self) -> int:
        return self._log_index