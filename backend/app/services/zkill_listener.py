"""zKillboard RedisQ listener for real-time kill feed."""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional
from datetime import datetime, timezone

import httpx

from ..core.config import settings
from .connection_manager import connection_manager
from .risk_engine import compute_risk

logger = logging.getLogger(__name__)


class ZKillListener:
    """Listens to zKillboard RedisQ for real-time kill data."""

    def __init__(
        self,
        queue_id: Optional[str] = None,
        on_kill: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.queue_id = queue_id or "eve-gatekeeper"
        self.on_kill = on_kill
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._reconnect_delay = 1  # Start with 1 second
        self._max_reconnect_delay = 60  # Max 60 seconds
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def is_running(self) -> bool:
        """Check if the listener is running."""
        return self._running

    async def start(self) -> None:
        """Start the listener."""
        if self._running:
            logger.warning("ZKill listener already running")
            return

        self._running = True
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout=35.0),  # RedisQ timeout is 30s
            headers={"User-Agent": settings.ZKILL_USER_AGENT},
        )
        self._task = asyncio.create_task(self._listen_loop())
        logger.info("ZKill listener started")

    async def stop(self) -> None:
        """Stop the listener."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("ZKill listener stopped")

    async def _listen_loop(self) -> None:
        """Main listening loop with reconnection logic."""
        while self._running:
            try:
                await self._fetch_kills()
                # Reset reconnect delay on successful fetch
                self._reconnect_delay = 1
            except asyncio.CancelledError:
                break
            except httpx.TimeoutException:
                # Timeout is normal - RedisQ returns after 30s with no data
                logger.debug("RedisQ timeout (normal), reconnecting...")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from zKillboard: {e.response.status_code}")
                await self._handle_reconnect()
            except Exception as e:
                logger.exception(f"Error in ZKill listener: {e}")
                await self._handle_reconnect()

    async def _handle_reconnect(self) -> None:
        """Handle reconnection with exponential backoff."""
        if not self._running:
            return

        logger.info(f"Reconnecting in {self._reconnect_delay} seconds...")
        await asyncio.sleep(self._reconnect_delay)

        # Exponential backoff
        self._reconnect_delay = min(
            self._reconnect_delay * 2,
            self._max_reconnect_delay,
        )

    async def _fetch_kills(self) -> None:
        """Fetch kills from RedisQ."""
        if not self._client:
            return

        url = f"{settings.ZKILL_REDISQ_URL}?queueID={self.queue_id}"

        response = await self._client.get(url)
        response.raise_for_status()

        data = response.json()
        package = data.get("package")

        if package is None:
            # No new kills available
            return

        # Process the kill
        await self._process_kill(package)

    async def _process_kill(self, package: Dict[str, Any]) -> None:
        """Process a kill package from zKillboard."""
        try:
            killmail = package.get("killmail", {})
            zkb = package.get("zkb", {})

            # Extract key information
            kill_id = killmail.get("killmail_id")
            solar_system_id = killmail.get("solar_system_id")
            kill_time = killmail.get("killmail_time")
            victim = killmail.get("victim", {})

            # Check if it's a pod kill
            ship_type_id = victim.get("ship_type_id")
            is_pod = ship_type_id in (670, 33328)  # Capsule, Genolution Capsule

            # Get system name from our data
            from .data_loader import load_universe
            universe = load_universe()
            system_name = None
            region_id = None

            for name, sys in universe.systems.items():
                if sys.id == solar_system_id:
                    system_name = name
                    region_id = sys.region_id
                    break

            # Compute risk score if we know the system
            risk_score = 0.0
            if system_name:
                try:
                    risk_report = compute_risk(system_name)
                    risk_score = risk_report.score
                except Exception:
                    pass

            # Build kill data
            kill_data = {
                "kill_id": kill_id,
                "solar_system_id": solar_system_id,
                "solar_system_name": system_name,
                "region_id": region_id,
                "kill_time": kill_time,
                "ship_type_id": ship_type_id,
                "is_pod": is_pod,
                "victim_corporation_id": victim.get("corporation_id"),
                "victim_alliance_id": victim.get("alliance_id"),
                "attacker_count": len(killmail.get("attackers", [])),
                "total_value": zkb.get("totalValue"),
                "points": zkb.get("points"),
                "npc": zkb.get("npc", False),
                "solo": zkb.get("solo", False),
                "risk_score": risk_score,
                "received_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.debug(
                f"Kill {kill_id} in {system_name or solar_system_id}: "
                f"{kill_data['total_value']:,.0f} ISK"
            )

            # Call custom handler if provided
            if self.on_kill:
                self.on_kill(kill_data)

            # Broadcast to connected WebSocket clients
            await connection_manager.broadcast_kill(kill_data)

        except Exception as e:
            logger.exception(f"Error processing kill: {e}")


# Global listener instance
_zkill_listener: Optional[ZKillListener] = None


def get_zkill_listener() -> ZKillListener:
    """Get or create the zKillboard listener instance."""
    global _zkill_listener
    if _zkill_listener is None:
        _zkill_listener = ZKillListener()
    return _zkill_listener
