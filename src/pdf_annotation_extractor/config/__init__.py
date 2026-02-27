#!/usr/bin/env python3
"""
PDF Annotation Extractor - Configuration Management
Copyright (C) 2024 Engin Karahan

Configuration management using KConfig (KDE) or fallback to QSettings/JSON.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import sys


class ConfigBackend(Enum):
    KCONFIG = "kconfig"
    QSETTINGS = "qsettings"
    JSON = "json"


@dataclass
class AppConfig:
    """Application configuration"""

    language: str = "en"
    last_directory: str = ""
    recent_files: list = field(default_factory=list)
    page_offset_default: int = -1
    output_format: str = "markdown"
    auto_detect_offset: bool = True
    window_width: int = 800
    window_height: int = 600
    theme: str = "system"

    MAX_RECENT_FILES: int = 10

    def add_recent_file(self, file_path: str) -> None:
        """Add a file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > self.MAX_RECENT_FILES:
            self.recent_files = self.recent_files[: self.MAX_RECENT_FILES]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ConfigManager:
    """Configuration manager with fallback support"""

    def __init__(self, app_name: str = "pdf-annotation-extractor"):
        self.app_name = app_name
        self.config: AppConfig = AppConfig()
        self._backend: Optional[Any] = None
        self._init_backend()

    def _init_backend(self) -> None:
        """Initialize configuration backend"""
        if self._try_kconfig():
            return

        if self._try_qsettings():
            return

        self._use_json_backend()

    def _try_kconfig(self) -> bool:
        """Try to use KConfig backend"""
        try:
            from PyQt6.QtCore import QCoreApplication
            from PyKDEConfig import KConfig

            config = KConfig(f"{self.app_name}rc", KConfig.SimpleConfig)
            self._backend = config
            self._load_from_backend()
            return True
        except ImportError:
            pass
        return False

    def _try_qsettings(self) -> bool:
        """Try to use QSettings backend"""
        try:
            from PyQt6.QtCore import QSettings

            self._qsettings = QSettings("karahan.net", self.app_name)
            self._load_from_qsettings()
            return True
        except ImportError:
            pass
        return False

    def _load_from_qsettings(self) -> None:
        """Load from QSettings"""
        if self._qsettings.contains("language"):
            self.config.language = self._qsettings.value("language", "en")
        if self._qsettings.contains("lastDirectory"):
            self.config.last_directory = self._qsettings.value("lastDirectory", "")
        if self._qsettings.contains("pageOffsetDefault"):
            self.config.page_offset_default = int(
                self._qsettings.value("pageOffsetDefault", -1)
            )
        if self._qsettings.contains("outputFormat"):
            self.config.output_format = self._qsettings.value(
                "outputFormat", "markdown"
            )
        if self._qsettings.contains("theme"):
            self.config.theme = self._qsettings.value("theme", "system")

    def _use_json_backend(self) -> bool:
        """Use JSON file backend as fallback"""
        config_dir = Path.home() / ".config" / self.app_name
        config_dir.mkdir(parents=True, exist_ok=True)
        self._config_path = config_dir / "config.json"
        self._backend = "json"
        self._load_from_backend()
        return True

    def _load_from_backend(self) -> None:
        """Load configuration from backend"""
        if self._backend == "json":
            if self._config_path.exists():
                try:
                    with open(self._config_path, "r") as f:
                        data = json.load(f)
                        self.config = AppConfig.from_dict(data)
                except Exception:
                    pass
            return

        if hasattr(self, "_qsettings"):
            self._load_from_qsettings()

    def save(self) -> None:
        """Save configuration to backend"""
        if self._backend == "json":
            with open(self._config_path, "w") as f:
                json.dump(self.config.to_dict(), f, indent=2)
            return

        if hasattr(self, "_qsettings"):
            self._qsettings.setValue("language", self.config.language)
            self._qsettings.setValue("lastDirectory", self.config.last_directory)
            self._qsettings.setValue(
                "pageOffsetDefault", self.config.page_offset_default
            )
            self._qsettings.setValue("outputFormat", self.config.output_format)
            self._qsettings.setValue("theme", self.config.theme)
            self._qsettings.sync()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return getattr(self.config, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        setattr(self.config, key, value)

    def add_recent_file(self, file_path: str) -> None:
        """Add a file to recent files list"""
        self.config.add_recent_file(file_path)

    def reset(self) -> None:
        """Reset to default configuration"""
        self.config = AppConfig()
        self.save()


_config_instance: Optional[ConfigManager] = None


def get_config(app_name: str = "pdf-annotation-extractor") -> ConfigManager:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(app_name)
    return _config_instance
