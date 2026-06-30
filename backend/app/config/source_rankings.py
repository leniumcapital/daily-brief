from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).parent / "source_rankings.yaml"


def load_source_rankings() -> dict:
    """Load category → ranked source list from YAML config."""
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f) or {}


def save_source_rankings(data: dict) -> None:
    with CONFIG_PATH.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
