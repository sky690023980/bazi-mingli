# -*- coding: utf-8 -*-
"""八字分析插件基类，所有术数/命理插件必须继承 BaziPlugin"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaziPlugin(ABC):
    """八字分析插件抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (unique identifier)"""
        ...

    @property
    def display_name(self) -> str:
        return self.name

    @property
    def description(self) -> str:
        return ""

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def enabled(self) -> bool:
        return True

    @abstractmethod
    def analyze(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Core analysis entry"""
        ...

    def get_tags(self) -> list:
        return []


class PluginRegistry:
    """Plugin registry singleton"""
    _instance: Optional['PluginRegistry'] = None
    _plugins: Dict[str, BaziPlugin] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, plugin: BaziPlugin) -> None:
        if not isinstance(plugin, BaziPlugin):
            raise TypeError("Plugin must inherit BaziPlugin")
        self._plugins[plugin.name] = plugin
        logger.info(f"Plugin registered: {plugin.name} v{plugin.version}")

    def get(self, name: str) -> Optional[BaziPlugin]:
        return self._plugins.get(name)

    def list_all(self) -> list:
        return list(self._plugins.values())

    def list_enabled(self) -> list:
        return [p for p in self._plugins.values() if p.enabled]

    def discover(self) -> int:
        try:
            from .qimen_plugin import QimenPlugin
            from .ziwei_plugin import ZiweiPlugin
            from .health_plugin import HealthPlugin
            from .marriage_plugin import MarriagePlugin
            self.register(QimenPlugin())
            self.register(ZiweiPlugin())
            self.register(HealthPlugin())
            self.register(MarriagePlugin())
        except ImportError as e:
            logger.warning(f"Some plugins failed: {e}")
        return len(self._plugins)


def get_registry() -> PluginRegistry:
    return PluginRegistry()
