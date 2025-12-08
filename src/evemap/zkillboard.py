"""zkillboard API client for fetching kill intel."""

import requests
from typing import Dict, List, Optional, Any
import time
import logging

logger = logging.getLogger(__name__)


class ZKillboardClient:
    """Client for fetching data from zkillboard.com API."""
    
    BASE_URL = "https://zkillboard.com/api"
    USER_AGENT = "EveMapMobile/0.1.0"
    
    def __init__(self, timeout: int = 10):
        """Initialize zkillboard client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
        self._last_request_time = 0
        self._min_request_interval = 1.0  # zkillboard rate limit: ~1 req/sec
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, endpoint: str) -> Optional[List[Dict[str, Any]]]:
        """Make a request to zkillboard API.
        
        Args:
            endpoint: API endpoint (without base URL)
            
        Returns:
            Response data or None on failure
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"zkillboard request failed: {e}")
            return None
    
    def get_system_kills(self, system_id: int, limit: int = 10) -> Dict[str, Any]:
        """Get recent kills in a system.
        
        Args:
            system_id: EVE system ID
            limit: Maximum number of kills to retrieve
            
        Returns:
            Dictionary with kill data and statistics
        """
        # zkillboard endpoint: /kills/solarSystemID/{id}/
        kills = self._make_request(f"/kills/solarSystemID/{system_id}/")
        
        if not kills:
            return {
                'system_id': system_id,
                'kills': [],
                'total_kills': 0,
                'danger_rating': 'unknown',
            }
        
        # Limit results
        kills = kills[:limit]
        
        # Process kills to extract relevant info
        processed_kills = []
        total_value = 0
        
        for kill in kills:
            killmail_id = kill.get('killmail_id', 0)
            zkb = kill.get('zkb', {})
            victim = kill.get('victim', {})
            
            kill_value = zkb.get('totalValue', 0)
            total_value += kill_value
            
            processed_kills.append({
                'killmail_id': killmail_id,
                'kill_time': kill.get('killmail_time', ''),
                'victim_ship_type': victim.get('ship_type_id', 0),
                'victim_id': victim.get('character_id', 0),
                'total_value': kill_value,
                'is_npc': zkb.get('npc', False),
                'is_solo': zkb.get('solo', False),
                'attacker_count': len(kill.get('attackers', [])),
            })
        
        # Calculate danger rating based on recent activity
        danger_rating = 'safe'
        if len(kills) > 5:
            danger_rating = 'moderate'
        if len(kills) > 10 or total_value > 1000000000:  # 1B ISK
            danger_rating = 'dangerous'
        
        return {
            'system_id': system_id,
            'kills': processed_kills,
            'total_kills': len(processed_kills),
            'total_value_destroyed': total_value,
            'danger_rating': danger_rating,
        }
    
    def get_character_kills(self, character_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent kills for a character.
        
        Args:
            character_id: EVE character ID
            limit: Maximum number of kills
            
        Returns:
            List of kill data
        """
        kills = self._make_request(f"/kills/characterID/{character_id}/")
        
        if not kills:
            return []
        
        return kills[:limit]
    
    def get_corporation_kills(self, corporation_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent kills for a corporation.
        
        Args:
            corporation_id: EVE corporation ID
            limit: Maximum number of kills
            
        Returns:
            List of kill data
        """
        kills = self._make_request(f"/kills/corporationID/{corporation_id}/")
        
        if not kills:
            return []
        
        return kills[:limit]
    
    def get_region_activity(self, region_id: int, limit: int = 20) -> Dict[str, Any]:
        """Get kill activity summary for a region.
        
        Args:
            region_id: EVE region ID
            limit: Maximum number of kills to analyze
            
        Returns:
            Dictionary with region activity statistics
        """
        kills = self._make_request(f"/kills/regionID/{region_id}/")
        
        if not kills:
            return {
                'region_id': region_id,
                'activity_level': 'unknown',
                'recent_kills': 0,
            }
        
        kills = kills[:limit]
        
        # Analyze activity
        total_value = sum(k.get('zkb', {}).get('totalValue', 0) for k in kills)
        
        activity_level = 'low'
        if len(kills) > 10:
            activity_level = 'moderate'
        if len(kills) > 15:
            activity_level = 'high'
        
        return {
            'region_id': region_id,
            'recent_kills': len(kills),
            'total_value_destroyed': total_value,
            'activity_level': activity_level,
        }
