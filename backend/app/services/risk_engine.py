"""Risk scoring engine."""

from backend.app.models.risk import RiskReport, ZKillStats
from backend.app.services.data_loader import load_universe, load_risk_config
from backend.app.services.zkill_client import fetch_system_stats


def compute_risk(system_name: str) -> RiskReport:
    """Compute risk score for a system."""
    universe = load_universe()
    config = load_risk_config()
    
    if system_name not in universe.systems:
        raise ValueError(f"System not found: {system_name}")
    
    system = universe.systems[system_name]
    zkill_stats = fetch_system_stats(system.system_id)
    
    # Calculate security score
    category = system.security_category
    security_weight = config.security_category_weights.get(category, 1.0)
    security_score = security_weight * (1.0 - system.security_status) * 20
    
    # Calculate kill score
    kill_weight = config.kill_weights.get("kills", 1.0)
    pod_weight = config.kill_weights.get("pods", 1.0)
    kill_score = kill_weight * zkill_stats.recent_kills
    pod_score = pod_weight * zkill_stats.recent_pods
    
    # Total risk score
    risk_score = security_score + kill_score + pod_score
    
    # Clamp risk score
    min_risk = config.clamp.get("min", 0)
    max_risk = config.clamp.get("max", 100)
    risk_score = max(min_risk, min(max_risk, risk_score))
    
    # Determine color
    risk_color = "green"
    for threshold_str, color in config.risk_colors.items():
        threshold = int(threshold_str)
        if risk_score >= threshold:
            risk_color = color
    
    return RiskReport(
        system_name=system_name,
        risk_score=risk_score,
        security_score=security_score,
        kill_score=kill_score,
        pod_score=pod_score,
        risk_color=risk_color
    )
