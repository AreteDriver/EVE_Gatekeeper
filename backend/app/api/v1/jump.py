"""Jump drive API v1 endpoints."""


from fastapi import APIRouter, HTTPException, Query

from ...models.jump import (
    JumpLegResponse,
    JumpRangeResponse,
    JumpRouteResponse,
    ShipType,
    SystemInRangeResponse,
    SystemsInRangeResponse,
)
from ...services.jump_drive import (
    CapitalShipType,
    calculate_distance_ly,
    calculate_jump_range,
    find_systems_in_range,
    plan_jump_route,
)

router = APIRouter()


@router.get(
    "/range",
    response_model=JumpRangeResponse,
    summary="Calculate jump range",
    description="Calculate jump range for a capital ship based on skills.",
)
def get_jump_range(
    ship: ShipType = Query(
        ShipType.JUMP_FREIGHTER,
        description="Capital ship type",
    ),
    jdc: int = Query(5, ge=0, le=5, description="Jump Drive Calibration level"),
    jfc: int = Query(5, ge=0, le=5, description="Jump Fuel Conservation level"),
) -> JumpRangeResponse:
    """
    Calculate jump range for a capital ship.

    - **ship**: Type of capital ship
    - **jdc**: Jump Drive Calibration skill level (0-5)
    - **jfc**: Jump Fuel Conservation skill level (0-5)
    """
    ship_type = CapitalShipType(ship.value)
    result = calculate_jump_range(ship_type, jdc, jfc)

    return JumpRangeResponse(
        ship_type=ship.value,
        base_range_ly=result.base_range_ly,
        max_range_ly=result.max_range_ly,
        jdc_level=result.jdc_level,
        jfc_level=result.jfc_level,
        fuel_per_ly=result.fuel_per_ly,
    )


@router.get(
    "/distance",
    summary="Calculate distance between systems",
    description="Calculate light year distance between two systems.",
)
def get_distance(
    from_system: str = Query(..., alias="from", description="Origin system"),
    to_system: str = Query(..., alias="to", description="Destination system"),
) -> dict:
    """Calculate light year distance between two systems."""
    try:
        distance = calculate_distance_ly(from_system, to_system)
        return {
            "from_system": from_system,
            "to_system": to_system,
            "distance_ly": round(distance, 2),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get(
    "/systems-in-range",
    response_model=SystemsInRangeResponse,
    summary="Find systems within jump range",
    description="Find all systems within jump range of origin.",
)
def get_systems_in_range(
    origin: str = Query(..., description="Origin system name"),
    ship: ShipType = Query(
        ShipType.JUMP_FREIGHTER,
        description="Capital ship type",
    ),
    jdc: int = Query(5, ge=0, le=5, description="Jump Drive Calibration level"),
    security: str | None = Query(
        None,
        description="Filter by security: 'lowsec' or 'nullsec'",
    ),
    limit: int = Query(50, ge=1, le=500, description="Max systems to return"),
) -> SystemsInRangeResponse:
    """
    Find all systems within jump range.

    - **origin**: Origin system name
    - **ship**: Capital ship type (determines base range)
    - **jdc**: Jump Drive Calibration level (0-5)
    - **security**: Optional filter - 'lowsec' or 'nullsec'
    - **limit**: Maximum number of systems to return
    """
    ship_type = CapitalShipType(ship.value)
    jump_range = calculate_jump_range(ship_type, jdc, 5)

    try:
        systems = find_systems_in_range(
            origin,
            jump_range.max_range_ly,
            security_filter=security,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    # Add fuel requirements
    for sys in systems:
        sys.fuel_required = int(sys.distance_ly * jump_range.fuel_per_ly)

    return SystemsInRangeResponse(
        origin=origin,
        max_range_ly=jump_range.max_range_ly,
        count=len(systems[:limit]),
        systems=[
            SystemInRangeResponse(
                name=s.name,
                system_id=s.system_id,
                distance_ly=s.distance_ly,
                security=s.security,
                category=s.category,
                fuel_required=s.fuel_required,
            )
            for s in systems[:limit]
        ],
    )


@router.get(
    "/route",
    response_model=JumpRouteResponse,
    summary="Plan jump route",
    description="Plan a capital ship jump route between two systems.",
)
def get_jump_route(
    from_system: str = Query(..., alias="from", description="Origin system"),
    to_system: str = Query(..., alias="to", description="Destination system"),
    ship: ShipType = Query(
        ShipType.JUMP_FREIGHTER,
        description="Capital ship type",
    ),
    jdc: int = Query(5, ge=0, le=5, description="Jump Drive Calibration level"),
    jfc: int = Query(5, ge=0, le=5, description="Jump Fuel Conservation level"),
    via: list[str] | None = Query(
        None,
        description="Specific midpoint systems to use",
    ),
) -> JumpRouteResponse:
    """
    Plan a jump route for a capital ship.

    - **from**: Origin system
    - **to**: Destination system
    - **ship**: Capital ship type
    - **jdc**: Jump Drive Calibration level (0-5)
    - **jfc**: Jump Fuel Conservation level (0-5)
    - **via**: Optional specific midpoint cyno systems
    """
    ship_type = CapitalShipType(ship.value)

    try:
        route = plan_jump_route(
            from_system,
            to_system,
            ship_type,
            jdc,
            jfc,
            midpoints=via,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    return JumpRouteResponse(
        from_system=route.from_system,
        to_system=route.to_system,
        ship_type=route.ship_type,
        total_jumps=route.total_jumps,
        total_distance_ly=route.total_distance_ly,
        total_fuel=route.total_fuel,
        total_fatigue_minutes=route.total_fatigue_minutes,
        total_travel_time_minutes=route.total_travel_time_minutes,
        legs=[
            JumpLegResponse(
                from_system=leg.from_system,
                to_system=leg.to_system,
                distance_ly=leg.distance_ly,
                fuel_required=leg.fuel_required,
                fatigue_added_minutes=leg.fatigue_added_minutes,
                total_fatigue_minutes=leg.total_fatigue_minutes,
                wait_time_minutes=leg.wait_time_minutes,
            )
            for leg in route.legs
        ],
    )
