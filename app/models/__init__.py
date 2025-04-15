import pkgutil
from pathlib import Path

from app.models.character import Character


def load_all_models() -> None:
    """Load all models from this folder."""
    package_dir = Path(__file__).resolve().parent
    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix="app.models.",
    )
    for module in modules:
        __import__(module.name)  # noqa: WPS421


__all__ = [
    "User",
    "UserPersona",
    "Character",
    "SettingsTemplate",
    "SettingsItemSpec",
    "SettingsInstance",
    "SettingsValue",
    "ChatSession",
    "ChatMessage",
]
