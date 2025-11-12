"""Caching utilities for ESI API responses."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class ESICache:
    """Simple file-based cache for ESI API responses."""

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cached data in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Sanitize key for filesystem
        safe_key = "".join(c if c.isalnum() or c in '-_' else '_' for c in key)
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/missing
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)

            # Check expiration
            cached_time = datetime.fromisoformat(data.get('timestamp', ''))
            if datetime.now() - cached_time > self.ttl:
                # Cache expired
                cache_path.unlink()
                return None

            return data.get('value')
        except (json.JSONDecodeError, KeyError, ValueError):
            # Cache corrupted
            cache_path.unlink()
            return None

    def set(self, key: str, value: Dict[str, Any]):
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(key)

        data = {
            'timestamp': datetime.now().isoformat(),
            'value': value
        }

        with open(cache_path, 'w') as f:
            json.dump(data, f)

    def clear(self):
        """Clear all cached data."""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()

    def cleanup(self):
        """Remove expired cache entries."""
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                cached_time = datetime.fromisoformat(data.get('timestamp', ''))
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
            except (json.JSONDecodeError, KeyError, ValueError):
                cache_file.unlink()
