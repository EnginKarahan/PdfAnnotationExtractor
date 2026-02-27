#!/usr/bin/env python3
"""
PDF Annotation Extractor - Plugin System
Copyright (C) 2024 Engin Karahan

Plugin system for extending PDF annotation processing capabilities.
Supports text processing, markdown export, and future plugins.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
import importlib
import pkgutil
import sys

from ..core import PDFAnnotation, AnnotationPlugin


@dataclass
class PluginMetadata:
    name: str
    version: str
    author: str
    description: str
    supported_formats: List[str]
    dependencies: List[str]


class PluginBase(ABC):
    """Base class for all plugins"""

    def __init__(self):
        self._metadata: Optional[PluginMetadata] = None

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration"""
        pass

    @abstractmethod
    def process(
        self, annotations: List[PDFAnnotation], context: dict
    ) -> List[PDFAnnotation]:
        """Process annotations"""
        pass

    def shutdown(self) -> None:
        """Cleanup when plugin is unloaded"""
        pass


class PluginManager:
    """Manages plugin loading and lifecycle"""

    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        self._plugins: Dict[str, AnnotationPlugin] = {}
        self._plugin_instances: Dict[str, PluginBase] = {}
        self._plugin_dirs = plugin_dirs or []
        self._config: Dict[str, Any] = {}

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set global configuration"""
        self._config = config

    def discover_plugins(self) -> List[str]:
        """Discover available plugins in plugin directories"""
        discovered = []
        for plugin_dir in self._plugin_dirs:
            if not plugin_dir.exists():
                continue
            for _, name, is_pkg in pkgutil.iter_modules([str(plugin_dir)]):
                discovered.append(name)
        return discovered

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name"""
        try:
            module = importlib.import_module(
                f"pdf_annotation_extractor.plugins.{plugin_name}"
            )
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, PluginBase)
                    and attr is not PluginBase
                ):
                    plugin_instance = attr()
                    if plugin_instance.initialize(self._config):
                        self._plugin_instances[plugin_name] = plugin_instance
                        return True
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
        return False

    def register_builtin_plugin(self, plugin: AnnotationPlugin) -> None:
        """Register a built-in plugin"""
        self._plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> Optional[AnnotationPlugin]:
        """Get loaded plugin by name"""
        if name in self._plugins:
            return self._plugins[name]
        if name in self._plugin_instances:
            return self._plugin_instances[name]
        return None

    def list_plugins(self) -> List[str]:
        """List all loaded plugin names"""
        return list(self._plugins.keys()) + list(self._plugin_instances.keys())

    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin"""
        if name in self._plugin_instances:
            self._plugin_instances[name].shutdown()
            del self._plugin_instances[name]
            return True
        if name in self._plugins:
            del self._plugins[name]
            return True
        return False


class MarkdownExportPlugin:
    """Plugin for enhanced Markdown export"""

    @property
    def name(self) -> str:
        return "markdown_export"

    @property
    def version(self) -> str:
        return "1.0.0"

    def process(
        self, annotations: List[PDFAnnotation], context: dict
    ) -> List[PDFAnnotation]:
        """Markdown export doesn't modify annotations"""
        return annotations

    def supports_format(self, output_format: str) -> bool:
        return output_format == "markdown"


class TextProcessingPlugin:
    """Plugin for text processing capabilities (future)"""

    @property
    def name(self) -> str:
        return "text_processing"

    @property
    def version(self) -> str:
        return "1.0.0"

    def process(
        self, annotations: List[PDFAnnotation], context: dict
    ) -> List[PDFAnnotation]:
        return annotations

    def supports_format(self, output_format: str) -> bool:
        return output_format in ("markdown", "text")
