"""Risk calculation engine with zKillboard integration."""

from ..models.risk import RiskBreakdown, RiskReport, ZKillStats
from .data_loader import load_risk_config, load_universe


def _calculate_risk_score(
    system_name: str,
    stats: ZKillStats,
) -> RiskReport:
    """
    Internal function to calculate risk score from system data and stats.

    Args:
        system_name: Name of the system
        stats: zKill stats for the system

    Returns:
        RiskReport with risk score and breakdown
    """
    cfg = load_risk_config()
    universe = load_universe()

    if system_name not in universe.systems:
        raise ValueError(f"Unknown system: {system_name}")

    system = universe.systems[system_name]

    security_weight = cfg.security_category_weights.get(system.category, 1.0)
    kills_w = cfg.kill_weights.get("recent_kills", 0.0)
    pods_w = cfg.kill_weights.get("recent_pods", 0.0)

    security_component = security_weight * (1.0 - system.security) * 20.0
    kills_component = kills_w * stats.recent_kills
    pods_component = pods_w * stats.recent_pods

    raw_score = security_component + kills_component + pods_component

    min_v = cfg.clamp["min"]
    max_v = cfg.clamp["max"]
    clamped = max(min_v, min(max_v, raw_score))

    breakdown = RiskBreakdown(
        security_component=security_component,
        kills_component=kills_component,
        pods_component=pods_component,
    )

    return RiskReport(
        system_name=system.name,
        system_id=system.id,
        category=system.category,
        security=system.security,
        score=clamped,
        breakdown=breakdown,
        zkill_stats=stats if (stats.recent_kills > 0 or stats.recent_pods > 0) else None,
    )


def compute_risk(system_name: str, stats: ZKillStats | None = None) -> RiskReport:
    """
    Compute risk score for a system (synchronous version).

    Uses cached zKill stats if available, otherwise uses static security-based scoring.

    Args:
        system_name: Name of the system
        stats: Optional pre-fetched zKill stats

    Returns:
        RiskReport with risk score and breakdown
    """
    if stats is None:
        # Try to get cached stats synchronously
        from .data_loader import load_universe
        from .zkill_stats import get_cached_stats_sync

        universe = load_universe()
        if system_name in universe.systems:
            system = universe.systems[system_name]
            cached_stats = get_cached_stats_sync(system.id)
            stats = cached_stats if cached_stats else ZKillStats()
        else:
            stats = ZKillStats()

    return _calculate_risk_score(system_name, stats)


async def compute_risk_async(
    system_name: str,
    fetch_live: bool = True,
) -> RiskReport:
    """
    Compute risk score for a system (async version with live zKill data).

    Args:
        system_name: Name of the system
        fetch_live: If True, fetch fresh data from zKillboard API

    Returns:
        RiskReport with risk score and breakdown
    """
    from .data_loader import load_universe
    from .zkill_stats import fetch_system_kills

    universe = load_universe()

    if system_name not in universe.systems:
        raise ValueError(f"Unknown system: {system_name}")

    system = universe.systems[system_name]

    if fetch_live:
        stats = await fetch_system_kills(system.id)
    else:
        stats = ZKillStats()

    return _calculate_risk_score(system_name, stats)


async def compute_route_risks_async(
    system_names: list[str],
    fetch_live: bool = True,
) -> dict[str, RiskReport]:
    """
    Compute risk scores for multiple systems efficiently.

    Fetches zKill stats in bulk to minimize API calls.

    Args:
        system_names: List of system names
        fetch_live: If True, fetch fresh data from zKillboard API

    Returns:
        Dict mapping system name to RiskReport
    """
    from .data_loader import load_universe
    from .zkill_stats import fetch_bulk_system_stats

    universe = load_universe()

    # Build list of system IDs
    system_ids = []
    name_to_id = {}
    for name in system_names:
        if name in universe.systems:
            system = universe.systems[name]
            system_ids.append(system.id)
            name_to_id[name] = system.id

    # Fetch stats in bulk
    if fetch_live and system_ids:
        stats_by_id = await fetch_bulk_system_stats(system_ids)
    else:
        stats_by_id = {}

    # Calculate risk for each system
    results = {}
    for name in system_names:
        if name in universe.systems:
            system_id = name_to_id.get(name)
            stats = stats_by_id.get(system_id, ZKillStats())
            results[name] = _calculate_risk_score(name, stats)

    return results


def risk_to_color(score: float) -> str:
    """Convert risk score to display color."""
    cfg = load_risk_config()
    for band, color in cfg.risk_colors.items():
        low, high = map(int, band.split("-"))
        if low <= score <= high:
            return color
    return "#FFFFFF"
