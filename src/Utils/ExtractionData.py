from __future__ import annotations

class ExtractionData:
    def __init__(self, action_name : str, recording_date : str, log_index : int):
        self._action_name = action_name
        self._recording_date = recording_date
        self._log_index = log_index

    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def recording_date(self) -> str:
        return self._recording_date

    @property
    def log_index(self) -> int:
        return self._log_index

    def __str__(self) -> str:
        return self._action_name + "/" + self._recording_date + "/" + str(self._log_index)