"""zKillboard client stub."""

from backend.app.models.risk import ZKillStats


def fetch_system_stats(system_id: int) -> ZKillStats:
    """Fetch kill statistics from zKillboard (stub implementation)."""
    # For MVP, return zero activity
    # TODO: Implement real HTTP calls to zKillboard API
    return ZKillStats(recent_kills=0, recent_pods=0)
