# -*- coding: utf-8 -*-
"""插件系统"""
from .base import BaziPlugin
from .health_plugin import HealthPlugin
from .marriage_plugin import MarriagePlugin

__all__ = ["BaziPlugin", "HealthPlugin", "MarriagePlugin"]
