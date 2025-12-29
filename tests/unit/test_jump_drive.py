"""Tests for jump drive calculations."""

import pytest

from backend.app.services.jump_drive import (
    SHIP_BASE_RANGE,
    SHIP_FUEL_PER_LY,
    CapitalShipType,
    JumpRange,
    calculate_jump_fatigue,
    calculate_jump_range,
)


class TestCapitalShipType:
    """Tests for CapitalShipType enum."""

    def test_all_ship_types_defined(self):
        """All capital ship types should be defined."""
        expected = [
            "jump_freighter",
            "carrier",
            "dreadnought",
            "force_auxiliary",
            "supercarrier",
            "titan",
            "rorqual",
            "black_ops",
        ]
        actual = [ship.value for ship in CapitalShipType]
        assert set(actual) == set(expected)

    def test_ship_types_have_base_range(self):
        """Every ship type should have a base range defined."""
        for ship_type in CapitalShipType:
            assert ship_type in SHIP_BASE_RANGE

    def test_ship_types_have_fuel_consumption(self):
        """Every ship type should have fuel consumption defined."""
        for ship_type in CapitalShipType:
            assert ship_type in SHIP_FUEL_PER_LY


class TestCalculateJumpRange:
    """Tests for calculate_jump_range function."""

    def test_jump_freighter_base_range(self):
        """Jump freighter should have 5 LY base range."""
        result = calculate_jump_range(CapitalShipType.JUMP_FREIGHTER, jdc_level=0, jfc_level=0)
        assert result.base_range_ly == 5.0

    def test_black_ops_base_range(self):
        """Black ops should have 4 LY base range."""
        result = calculate_jump_range(CapitalShipType.BLOPS, jdc_level=0, jfc_level=0)
        assert result.base_range_ly == 4.0

    def test_jdc_increases_range(self):
        """JDC skill should increase range by 25% per level."""
        result_0 = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=0, jfc_level=0)
        result_5 = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=5, jfc_level=0)

        # JDC 5 = 125% bonus = 2.25x base range
        expected_max = result_0.base_range_ly * 2.25
        assert result_5.max_range_ly == expected_max

    def test_jdc_level_1_bonus(self):
        """JDC level 1 should give 25% bonus."""
        result = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=1, jfc_level=0)
        assert result.max_range_ly == 5.0 * 1.25

    def test_jdc_level_3_bonus(self):
        """JDC level 3 should give 75% bonus."""
        result = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=3, jfc_level=0)
        assert result.max_range_ly == 5.0 * 1.75

    def test_jfc_reduces_fuel(self):
        """JFC skill should reduce fuel by 10% per level."""
        result_0 = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=5, jfc_level=0)
        result_5 = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=5, jfc_level=5)

        # JFC 5 = 50% reduction
        assert result_5.fuel_per_ly == int(result_0.fuel_per_ly * 0.5)

    def test_jfc_level_1_reduction(self):
        """JFC level 1 should give 10% fuel reduction."""
        result = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=0, jfc_level=1)
        base_fuel = SHIP_FUEL_PER_LY[CapitalShipType.CARRIER]
        assert result.fuel_per_ly == int(base_fuel * 0.9)

    def test_returns_jump_range_dataclass(self):
        """Should return a JumpRange dataclass."""
        result = calculate_jump_range(CapitalShipType.TITAN, jdc_level=5, jfc_level=5)
        assert isinstance(result, JumpRange)
        assert hasattr(result, 'base_range_ly')
        assert hasattr(result, 'max_range_ly')
        assert hasattr(result, 'jdc_level')
        assert hasattr(result, 'jfc_level')
        assert hasattr(result, 'fuel_per_ly')

    def test_titan_higher_fuel_consumption(self):
        """Titans should have higher fuel consumption than carriers."""
        titan = calculate_jump_range(CapitalShipType.TITAN, jdc_level=0, jfc_level=0)
        carrier = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=0, jfc_level=0)
        assert titan.fuel_per_ly > carrier.fuel_per_ly

    def test_blops_lower_fuel_consumption(self):
        """Black ops should have lower fuel consumption."""
        blops = calculate_jump_range(CapitalShipType.BLOPS, jdc_level=0, jfc_level=0)
        carrier = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=0, jfc_level=0)
        assert blops.fuel_per_ly < carrier.fuel_per_ly

    def test_skill_levels_stored_in_result(self):
        """Skill levels should be stored in the result."""
        result = calculate_jump_range(CapitalShipType.CARRIER, jdc_level=3, jfc_level=4)
        assert result.jdc_level == 3
        assert result.jfc_level == 4


class TestCalculateJumpFatigue:
    """Tests for calculate_jump_fatigue function."""

    def test_no_current_fatigue(self):
        """First jump should add fatigue based on distance."""
        fatigue_added, total_fatigue, wait_time = calculate_jump_fatigue(5.0, 0)

        assert fatigue_added > 0
        assert total_fatigue == fatigue_added
        assert wait_time > 0

    def test_fatigue_increases_with_distance(self):
        """Longer jumps should add more fatigue."""
        short_jump = calculate_jump_fatigue(2.0, 0)
        long_jump = calculate_jump_fatigue(8.0, 0)

        assert long_jump[0] > short_jump[0]  # fatigue_added

    def test_fatigue_accumulates(self):
        """Fatigue should accumulate across multiple jumps."""
        _, fatigue_1, _ = calculate_jump_fatigue(5.0, 0)
        _, fatigue_2, _ = calculate_jump_fatigue(5.0, fatigue_1)

        assert fatigue_2 > fatigue_1

    def test_fatigue_capped(self):
        """Fatigue should be capped at 3000 minutes."""
        _, total_fatigue, _ = calculate_jump_fatigue(10.0, 2900)

        assert total_fatigue <= 3000

    def test_wait_time_increases_with_fatigue(self):
        """Wait time should increase when fatigue is higher."""
        _, _, wait_1 = calculate_jump_fatigue(5.0, 0)
        _, _, wait_2 = calculate_jump_fatigue(5.0, 500)

        assert wait_2 > wait_1

    def test_returns_tuple_of_three(self):
        """Should return a tuple of three values."""
        result = calculate_jump_fatigue(5.0, 100)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_all_values_are_floats(self):
        """All returned values should be floats."""
        fatigue_added, total_fatigue, wait_time = calculate_jump_fatigue(5.0, 100)

        assert isinstance(fatigue_added, float)
        assert isinstance(total_fatigue, float)
        assert isinstance(wait_time, float)

    def test_zero_distance_jump(self):
        """Zero distance jump should add minimal fatigue."""
        fatigue_added, _, _ = calculate_jump_fatigue(0.0, 0)
        assert fatigue_added == 0.0


class TestShipBaseRanges:
    """Tests for ship base range constants."""

    def test_capitals_have_5ly_base(self):
        """Most capitals should have 5 LY base range."""
        capitals_5ly = [
            CapitalShipType.JUMP_FREIGHTER,
            CapitalShipType.CARRIER,
            CapitalShipType.DREADNOUGHT,
            CapitalShipType.FORCE_AUXILIARY,
            CapitalShipType.SUPERCARRIER,
            CapitalShipType.TITAN,
            CapitalShipType.RORQUAL,
        ]
        for ship in capitals_5ly:
            assert SHIP_BASE_RANGE[ship] == 5.0

    def test_blops_has_4ly_base(self):
        """Black ops should have 4 LY base range."""
        assert SHIP_BASE_RANGE[CapitalShipType.BLOPS] == 4.0


class TestShipFuelConsumption:
    """Tests for ship fuel consumption constants."""

    def test_standard_capitals_fuel(self):
        """Standard capitals should use 1000 fuel per LY."""
        standard_capitals = [
            CapitalShipType.JUMP_FREIGHTER,
            CapitalShipType.CARRIER,
            CapitalShipType.DREADNOUGHT,
            CapitalShipType.FORCE_AUXILIARY,
        ]
        for ship in standard_capitals:
            assert SHIP_FUEL_PER_LY[ship] == 1000

    def test_supercarrier_fuel(self):
        """Supercarriers should use 1500 fuel per LY."""
        assert SHIP_FUEL_PER_LY[CapitalShipType.SUPERCARRIER] == 1500

    def test_titan_fuel(self):
        """Titans should use 2500 fuel per LY."""
        assert SHIP_FUEL_PER_LY[CapitalShipType.TITAN] == 2500

    def test_rorqual_fuel(self):
        """Rorquals should use 1200 fuel per LY."""
        assert SHIP_FUEL_PER_LY[CapitalShipType.RORQUAL] == 1200

    def test_blops_fuel(self):
        """Black ops should use 300 fuel per LY."""
        assert SHIP_FUEL_PER_LY[CapitalShipType.BLOPS] == 300
