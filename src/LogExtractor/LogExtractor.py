from __future__ import annotations
from pathlib import Path
from typing import Optional

class LogExtractor:
    def __init__(self):
        pass

    def extract_log(self, path : Path):
        pass

    def extract_recursive(self, path : Path):
        pass

    def extract_logs(self, action_type : Optional[str] = None, date : Optional[str] = None, log_index : Optional[int] = None):
        pass
