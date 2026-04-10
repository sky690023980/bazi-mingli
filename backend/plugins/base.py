# -*- coding: utf-8 -*-
"""插件基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaziPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    def display_name(self) -> str:
        return self.name

    @property
    def description(self) -> str:
        return ""

    @abstractmethod
    def analyze(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        ...
