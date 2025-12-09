from .data_loader import load_risk_config, load_universe
from ..models.risk import ZKillStats, RiskReport, RiskBreakdown


def compute_risk(system_name: str, stats: ZKillStats | None = None) -> RiskReport:
    cfg = load_risk_config()
    universe = load_universe()

    if system_name not in universe.systems:
        raise ValueError(f"Unknown system: {system_name}")

    system = universe.systems[system_name]
    stats = stats or ZKillStats()

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
    )


def risk_to_color(score: float) -> str:
    cfg = load_risk_config()
    for band, color in cfg.risk_colors.items():
        low, high = map(int, band.split("-"))
        if low <= score <= high:
            return color
    return "#FFFFFF"
