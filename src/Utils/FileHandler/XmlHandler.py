from __future__ import annotations
from abc import abstractmethod
from typing import override
import xml.etree.ElementTree as ET
from pathlib import Path

from .FileHandler import FileHandler

class XmlHandler(FileHandler):
    def __init__(self, path: Path):
        self._xml_tree: ET.ElementTree = ET.ElementTree()
        super().__init__(path)

    @override
    def _load_from_file(self):
        self._xml_tree = ET.parse(self._path)
        self._xml_to_dict()

    @override
    def _write_to_file(self):
        self._dict_to_xml()
        self._xml_tree.write(self._path)

    @abstractmethod
    def _xml_to_dict(self):
        pass

    @abstractmethod
    def _dict_to_xml(self):
        pass