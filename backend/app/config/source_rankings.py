from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).parent
SOURCES_PATH = CONFIG_DIR / "sources.yaml"
RANKINGS_PATH = CONFIG_DIR / "source_rankings.yaml"


def load_sources_config() -> dict:
    if not SOURCES_PATH.exists():
        return {}
    with SOURCES_PATH.open() as f:
        return yaml.safe_load(f) or {}


def load_source_rankings() -> dict:
    """Backward-compatible loader; prefers unified sources.yaml."""
    config = load_sources_config()
    if config.get("category_rankings"):
        return {
            "category_rankings": config["category_rankings"],
            "rss_feeds": _legacy_rss_map(config.get("sources", {})),
            "twitter": config.get("twitter", {}),
        }
    if RANKINGS_PATH.exists():
        with RANKINGS_PATH.open() as f:
            return yaml.safe_load(f) or {}
    return {}


def _legacy_rss_map(sources: dict) -> dict:
    feeds = {}
    for name, meta in sources.items():
        for provider in meta.get("providers", []):
            if provider.get("type") == "rss" and provider.get("url"):
                feeds[name] = {"url": provider["url"], "category": meta["category"]}
                break
    return feeds


def get_all_sources() -> dict:
    return load_sources_config().get("sources", {})


def get_twitter_config() -> dict:
    return load_sources_config().get("twitter", {"accounts": [], "keywords": []})
