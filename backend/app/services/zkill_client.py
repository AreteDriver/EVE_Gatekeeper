from ..models.risk import ZKillStats


async def fetch_system_stats(system_id: int) -> ZKillStats:
    """
    Stub for zKillboard integration.
    Copilot: implement HTTP calls to zKillboard later.
    For now, return zero activity so we can work offline.
    """
    return ZKillStats()
