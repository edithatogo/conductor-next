from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError


class FeatureFlags(BaseModel):
    """Experimental and next-gen feature flags."""

    # Conductor Next Features
    enable_beta_sync: bool = True
    enable_vcs_agnostic: bool = False
    enable_ralph_loop: bool = False
    enable_plan_mode_warning: bool = True
    enable_artifact_inference: bool = False

    # Custom extensions
    custom_flags: dict[str, bool] = {}


class ConductorConfig(BaseModel):
    """Configuration model for Conductor."""

    version: str = "1.0-next"
    project_name: str = ""
    description: str = ""
    default_track_template: str = "default"
    enable_git_integration: bool = True
    enable_locking: bool = True
    default_workflow: str = "standard"
    extensions: dict[str, Any] = {}
    feature_flags: FeatureFlags = FeatureFlags()
    templates_path: str = "./templates"
    tracks_path: str = "./tracks"
    archive_path: str = "./archive"


class ConfigManager:
    """Manages conductor configuration."""

    def __init__(self, base_path: str | Path = "."):
        self.base_path = Path(base_path)
        self.conductor_path = self.base_path / "conductor"
        self.config_file = self.conductor_path / "config.json"
        self._config: ConductorConfig | None = None

    def load_config(self) -> ConductorConfig:
        """Load configuration from config.json file."""
        if self._config is not None:
            return self._config

        if self.config_file.exists():
            try:
                content = self.config_file.read_text(encoding="utf-8")
                data = json.loads(content)
                self._config = ConductorConfig(**data)
            except (json.JSONDecodeError, ValidationError) as e:
                # Handle migrations or default if config is old
                self._config = ConductorConfig()
                self.save_config()
            except Exception as e:
                raise ValueError(f"Invalid configuration in {self.config_file}: {e}") from e
        else:
            # Create default configuration
            self._config = ConductorConfig()
            self.save_config()

        return self._config

    def is_feature_enabled(self, flag_name: str) -> bool:
        """Check if a specific feature flag is enabled."""
        config = self.load_config()
        flags = config.feature_flags
        
        # Check standard flags
        if hasattr(flags, flag_name):
            return getattr(flags, flag_name)
            
        # Check custom flags
        return flags.custom_flags.get(flag_name, False)

    def save_config(self, config: ConductorConfig | None = None) -> None:
        """Save configuration to config.json file."""
        if config is not None:
            self._config = config
        elif self._config is None:
            self._config = ConductorConfig()

        # Ensure conductor directory exists
        self.conductor_path.mkdir(parents=True, exist_ok=True)

        # Write config to file
        with self.config_file.open("w", encoding="utf-8") as f:
            f.write(self._config.model_dump_json(indent=2))

    def update_config(self, **kwargs) -> ConductorConfig:
        """Update configuration with provided values."""
        config = self.load_config()

        # Update fields
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.save_config(config)
        return config

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value."""
        config = self.load_config()
        return getattr(config, key, default)
