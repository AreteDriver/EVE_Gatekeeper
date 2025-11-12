"""Heatmap data layer for live universe activity."""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path
import requests
from .cache import ESICache
from .database import DatabaseManager


class HeatmapEngine:
    """Manage heatmap data from ESI /universe endpoints."""

    # ESI endpoints for heatmap data
    ESI_KILLS_URL = "https://esi.eveonline.com/latest/universe/system_kills/"
    ESI_JUMPS_URL = "https://esi.eveonline.com/latest/universe/system_jumps/"
    ESI_INCURSIONS_URL = "https://esi.eveonline.com/latest/incursions/"
    ESI_SOV_URL = "https://esi.eveonline.com/latest/sovereignty/map/"
    ESI_CAMPAIGNS_URL = "https://esi.eveonline.com/latest/sovereignty/campaigns/"

    def __init__(self, db_manager: DatabaseManager, cache_ttl_hours: int = 6):
        """Initialize heatmap engine.

        Args:
            db_manager: DatabaseManager instance
            cache_ttl_hours: TTL for cached heatmap data
        """
        self.db = db_manager
        self.cache = ESICache(cache_dir="data/heatmap_cache", ttl_hours=cache_ttl_hours)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "EveMapVisualization/1.0.0"})

    def _fetch_esi(self, url: str, cache_key: str = None, retries: int = 3) -> Optional[List[Dict]]:
        """Fetch data from ESI with caching.

        Args:
            url: ESI endpoint URL
            cache_key: Cache key (uses URL if not provided)
            retries: Number of retries on failure

        Returns:
            Response data or None
        """
        if not cache_key:
            cache_key = url.split('/')[-2]

        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Fetch from ESI
        for attempt in range(retries):
            try:
                print(f"  Fetching {url}...")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                data = response.json()

                # Cache result
                self.cache.set(cache_key, data)

                return data

            except requests.RequestException as e:
                if attempt < retries - 1:
                    import time
                    wait_time = 2 ** attempt
                    print(f"    Error: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"    Failed after {retries} retries: {e}")
                    return None

    def get_system_kills(self) -> Dict[int, int]:
        """Get kill counts per system (last 24h).

        Returns:
            Dict mapping system_id to kill_count
        """
        print("Fetching system kills from ESI...")

        data = self._fetch_esi(self.ESI_KILLS_URL, cache_key="system_kills")
        if not data:
            return {}

        # Convert to dict for easier lookup
        return {item['system_id']: item['ship_kills'] + item['npc_kills']
                for item in data if 'system_id' in item}

    def get_system_jumps(self) -> Dict[int, int]:
        """Get jump counts per system (last 24h).

        Returns:
            Dict mapping system_id to jump_count
        """
        print("Fetching system jumps from ESI...")

        data = self._fetch_esi(self.ESI_JUMPS_URL, cache_key="system_jumps")
        if not data:
            return {}

        # Convert to dict for easier lookup
        return {item['system_id']: item['ship_jumps']
                for item in data if 'system_id' in item}

    def get_incursions(self) -> List[Dict]:
        """Get active incursions in New Eden.

        Returns:
            List of incursion data
        """
        print("Fetching incursion data from ESI...")

        data = self._fetch_esi(self.ESI_INCURSIONS_URL, cache_key="incursions")
        if not data:
            return []

        # Normalize incursion data
        return [{
            'id': inc.get('incursion_id'),
            'state': inc.get('state'),
            'type': inc.get('type'),
            'faction': inc.get('faction_id'),
            'influence': inc.get('influence', 0.0),
            'staging_system': inc.get('staging_solar_system_id'),
            'systems': inc.get('infested_solar_systems', []),
            'has_boss': inc.get('has_boss', False),
        } for inc in data if 'incursion_id' in inc]

    def get_sovereignty_map(self) -> Dict[int, Dict]:
        """Get sovereignty data for regions.

        Returns:
            Dict mapping system_id to sovereignty data
        """
        print("Fetching sovereignty map from ESI...")

        data = self._fetch_esi(self.ESI_SOV_URL, cache_key="sovereignty_map")
        if not data:
            return {}

        # Convert to dict by system ID
        result = {}
        for item in data:
            if 'system_id' in item:
                result[item['system_id']] = {
                    'alliance_id': item.get('alliance_id'),
                    'faction_id': item.get('faction_id'),
                    'corporation_id': item.get('corporation_id'),
                }

        return result

    def get_sov_campaigns(self) -> List[Dict]:
        """Get active sovereignty campaigns.

        Returns:
            List of campaign data
        """
        print("Fetching sov campaigns from ESI...")

        data = self._fetch_esi(self.ESI_CAMPAIGNS_URL, cache_key="sov_campaigns")
        if not data:
            return []

        # Normalize campaign data
        return [{
            'id': camp.get('campaign_id'),
            'type': camp.get('type'),
            'system_id': camp.get('solar_system_id'),
            'constellation_id': camp.get('constellation_id'),
            'region_id': camp.get('region_id'),
            'defending_id': camp.get('defender_id'),
            'attacking_id': camp.get('attacker_id'),
            'start_time': camp.get('start_time'),
            'contested': camp.get('contested', False),
        } for camp in data if 'campaign_id' in camp]

    def normalize_heatmap(self, values: Dict[int, int], max_value: Optional[int] = None) -> Dict[int, float]:
        """Normalize heatmap values to 0-1 range.

        Args:
            values: Raw values dict
            max_value: Maximum value (uses actual max if not provided)

        Returns:
            Normalized dict with 0-1 values
        """
        if not values:
            return {}

        if max_value is None:
            max_value = max(values.values()) if values else 1

        if max_value == 0:
            return {k: 0.0 for k in values.keys()}

        return {k: min(1.0, v / max_value) for k, v in values.items()}

    def get_activity_heatmap(self) -> Dict[str, Dict[int, float]]:
        """Get combined activity heatmap (kills + jumps).

        Returns:
            Dict with 'kills' and 'jumps' normalized heatmaps
        """
        print("\nFetching activity heatmap...")

        kills = self.get_system_kills()
        jumps = self.get_system_jumps()

        return {
            'kills': self.normalize_heatmap(kills),
            'jumps': self.normalize_heatmap(jumps),
            'timestamp': datetime.now().isoformat(),
        }

    def get_intel_layers(self) -> Dict[str, any]:
        """Get all intel layers for map visualization.

        Returns:
            Complete intel data (activity, incursions, sov, campaigns)
        """
        print("\n" + "=" * 70)
        print("FETCHING LIVE INTEL LAYERS")
        print("=" * 70)

        result = {
            'timestamp': datetime.now().isoformat(),
            'activity': {},
            'incursions': [],
            'sovereignty': {},
            'campaigns': [],
        }

        # Activity heatmap
        activity = self.get_activity_heatmap()
        result['activity'] = activity

        # Incursions
        incursions = self.get_incursions()
        result['incursions'] = incursions
        print(f"Found {len(incursions)} active incursions")

        # Sovereignty
        sov = self.get_sovereignty_map()
        result['sovereignty'] = sov
        print(f"Loaded sovereignty data for {len(sov)} systems")

        # Sov campaigns
        campaigns = self.get_sov_campaigns()
        result['campaigns'] = campaigns
        print(f"Found {len(campaigns)} active sov campaigns")

        print()

        return result

    def export_heatmap_json(self, filepath: str = "data/heatmap_data.json"):
        """Export heatmap data as JSON for mobile clients.

        Args:
            filepath: Output file path
        """
        print(f"Exporting heatmap data to {filepath}...")

        data = self.get_intel_layers()

        # Create directory if needed
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(data, f, separators=(',', ':'))

        print(f"✓ Exported heatmap data")
