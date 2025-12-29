"""zKillboard statistics service for dynamic risk scoring."""

import asyncio
import logging
from datetime import UTC, datetime

import httpx

from ..core.config import settings
from ..models.risk import ZKillStats
from .cache import get_cache, get_cache_sync

logger = logging.getLogger(__name__)

# Cache TTL for zKill stats (10 minutes - balance between freshness and API limits)
ZKILL_STATS_TTL = 600

# Track rate limiting
_last_request_time: datetime = datetime.min.replace(tzinfo=UTC)
_request_interval = 1.0  # Minimum seconds between requests (zKill asks for 1 req/sec)


def build_zkill_stats_key(system_id: int) -> str:
    """Build cache key for zKill stats."""
    return f"zkill:stats:{system_id}"


async def _rate_limit() -> None:
    """Enforce rate limiting for zKillboard API."""
    global _last_request_time
    now = datetime.now(UTC)
    elapsed = (now - _last_request_time).total_seconds()

    if elapsed < _request_interval:
        await asyncio.sleep(_request_interval - elapsed)

    _last_request_time = datetime.now(UTC)


async def fetch_system_kills(system_id: int, hours: int = 24) -> ZKillStats:
    """
    Fetch recent kill statistics for a system from zKillboard.

    Args:
        system_id: EVE system ID
        hours: Number of hours to look back (default 24)

    Returns:
        ZKillStats with recent_kills and recent_pods counts
    """
    cache = await get_cache()
    cache_key = build_zkill_stats_key(system_id)

    # Check cache first
    cached = await cache.get_json(cache_key)
    if cached is not None:
        logger.debug(f"Cache hit for system {system_id} zkill stats")
        return ZKillStats(**cached)

    # Fetch from zKillboard API
    await _rate_limit()

    # Use the kills endpoint with pastSeconds filter
    # zKillboard API: /api/kills/solarSystemID/{id}/pastSeconds/{seconds}/
    past_seconds = hours * 3600
    url = f"{settings.ZKILL_BASE_URL}/kills/solarSystemID/{system_id}/pastSeconds/{past_seconds}/"

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            headers={"User-Agent": settings.ZKILL_USER_AGENT}
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            kills = response.json()

            if not isinstance(kills, list):
                kills = []

            # Count kills and pods
            recent_kills = 0
            recent_pods = 0

            for kill in kills:
                victim = kill.get("victim", {})
                ship_type_id = victim.get("ship_type_id", 0)

                # Pod type IDs: 670 (Capsule), 33328 (Genolution Capsule)
                if ship_type_id in (670, 33328):
                    recent_pods += 1
                else:
                    recent_kills += 1

            stats = ZKillStats(recent_kills=recent_kills, recent_pods=recent_pods)

            # Cache the result
            await cache.set_json(cache_key, stats.model_dump(), ZKILL_STATS_TTL)

            logger.debug(f"Fetched zkill stats for system {system_id}: {recent_kills} kills, {recent_pods} pods")
            return stats

    except httpx.TimeoutException:
        logger.warning(f"Timeout fetching zKill stats for system {system_id}")
        return ZKillStats()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            logger.warning("zKillboard rate limit hit, backing off")
        else:
            logger.warning(f"HTTP error fetching zKill stats for {system_id}: {e.response.status_code}")
        return ZKillStats()
    except Exception as e:
        logger.exception(f"Error fetching zKill stats for system {system_id}: {e}")
        return ZKillStats()


async def fetch_bulk_system_stats(system_ids: list[int], hours: int = 24) -> dict[int, ZKillStats]:
    """
    Fetch kill stats for multiple systems efficiently.

    Uses caching to avoid redundant API calls.

    Args:
        system_ids: List of EVE system IDs
        hours: Number of hours to look back

    Returns:
        Dict mapping system_id to ZKillStats
    """
    results: dict[int, ZKillStats] = {}
    cache = await get_cache()

    # First pass: check cache
    uncached_ids = []
    for system_id in system_ids:
        cache_key = build_zkill_stats_key(system_id)
        cached = await cache.get_json(cache_key)
        if cached is not None:
            results[system_id] = ZKillStats(**cached)
        else:
            uncached_ids.append(system_id)

    # Second pass: fetch uncached (with rate limiting)
    for system_id in uncached_ids:
        stats = await fetch_system_kills(system_id, hours)
        results[system_id] = stats

    return results


def get_cached_stats_sync(system_id: int) -> ZKillStats | None:
    """
    Get cached zKill stats synchronously (for use in sync code paths).

    Returns None if not cached - does not fetch from API.
    """
    cache = get_cache_sync()
    cache_key = build_zkill_stats_key(system_id)

    # Synchronous cache access - only works with memory cache
    if hasattr(cache, '_caches'):
        for ttl_cache in cache._caches.values():
            if cache_key in ttl_cache:
                import json
                try:
                    data = json.loads(ttl_cache[cache_key])
                    return ZKillStats(**data)
                except (json.JSONDecodeError, KeyError):
                    pass

    return None


# Background task for preloading stats
class ZKillStatsPreloader:
    """Background service to preload zKill stats for high-traffic systems."""

    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None
        # High-traffic systems to preload (major trade hubs and pipe systems)
        self._priority_systems = [
            30000142,  # Jita
            30002187,  # Amarr
            30002659,  # Dodixie
            30002510,  # Rens
            30002053,  # Hek
            30002813,  # Tama
            30002718,  # Rancer
            30002537,  # Amamake
            30003504,  # Niarja (RIP)
            30005196,  # Ahbazon
        ]

    async def start(self) -> None:
        """Start the preloader background task."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._preload_loop())
        logger.info("ZKill stats preloader started")

    async def stop(self) -> None:
        """Stop the preloader."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("ZKill stats preloader stopped")

    async def _preload_loop(self) -> None:
        """Main preload loop."""
        while self._running:
            try:
                logger.debug("Preloading zKill stats for priority systems")
                await fetch_bulk_system_stats(self._priority_systems)
                # Wait before next refresh
                await asyncio.sleep(ZKILL_STATS_TTL // 2)  # Refresh at half TTL
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in zKill preloader: {e}")
                await asyncio.sleep(60)  # Wait a minute on error


# Global preloader instance
_preloader: ZKillStatsPreloader | None = None


def get_zkill_preloader() -> ZKillStatsPreloader:
    """Get or create the zKill stats preloader instance."""
    global _preloader
    if _preloader is None:
        _preloader = ZKillStatsPreloader()
    return _preloader
