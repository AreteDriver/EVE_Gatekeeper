"""Unit tests for risk engine."""

import pytest

from backend.app.models.risk import ZKillStats
from backend.app.services.risk_engine import compute_risk, risk_to_color


class TestComputeRisk:
    """Tests for compute_risk function."""

    def test_compute_risk_highsec_system(self):
        """Test risk calculation for a high-sec system."""
        report = compute_risk("Jita")

        assert report.system_name == "Jita"
        assert report.system_id == 30000142
        assert report.category == "highsec"
        assert report.security == 0.95  # Real Jita security
        # High-sec with no kills should have low risk
        assert 0 <= report.score <= 100

    def test_compute_risk_lowsec_system(self):
        """Test risk calculation for a low-sec system."""
        report = compute_risk("Tama")  # Use Tama instead of Niarja (real lowsec)

        assert report.system_name == "Tama"
        assert report.category == "lowsec"
        assert 0.0 < report.security < 0.5  # Lowsec range
        # Low-sec should have higher base risk than high-sec
        assert report.score > 0

    def test_compute_risk_with_kill_stats(self):
        """Test risk calculation with kill statistics."""
        stats_high = ZKillStats(recent_kills=500, recent_pods=100)
        stats_low = ZKillStats(recent_kills=0, recent_pods=0)
        report_with_kills = compute_risk("Jita", stats=stats_high)
        report_no_kills = compute_risk("Jita", stats=stats_low)

        # Risk should be higher with kills
        assert report_with_kills.score > report_no_kills.score

    def test_compute_risk_unknown_system(self):
        """Test risk calculation for unknown system raises error."""
        with pytest.raises(ValueError, match="Unknown system"):
            compute_risk("NonExistentSystem")

    def test_compute_risk_breakdown(self):
        """Test that risk breakdown is properly populated."""
        stats = ZKillStats(recent_kills=10, recent_pods=5)
        report = compute_risk("Jita", stats=stats)

        assert report.breakdown.security_component >= 0
        assert report.breakdown.kills_component >= 0
        assert report.breakdown.pods_component >= 0

    def test_compute_risk_clamped(self):
        """Test that risk score is clamped between 0 and 100."""
        # Even with extreme kill stats, should not exceed 100
        extreme_stats = ZKillStats(recent_kills=10000, recent_pods=5000)
        report = compute_risk("Tama", stats=extreme_stats)

        assert 0 <= report.score <= 100


class TestRiskToColor:
    """Tests for risk_to_color function."""

    def test_low_risk_color(self):
        """Test color for low risk score."""
        color = risk_to_color(5)
        assert color == "#3AF57A"  # Green

    def test_medium_risk_color(self):
        """Test color for medium risk score."""
        color = risk_to_color(30)
        assert color == "#F5D33A"  # Yellow

    def test_high_risk_color(self):
        """Test color for high risk score."""
        color = risk_to_color(80)
        assert color == "#F53A3A"  # Red

    def test_boundary_risk_color(self):
        """Test color at exact boundary."""
        color = risk_to_color(10)
        assert color == "#3AF57A"  # Should be in 0-10 band

    def test_out_of_range_color(self):
        """Test color for out-of-range score returns default."""
        color = risk_to_color(150)
        assert color == "#FFFFFF"  # Default white
