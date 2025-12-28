"""Jump bridge API v1 endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException, Query

from ...services.jumpbridge import (
    load_bridge_config,
    import_bridges,
    toggle_network,
    delete_network,
    clear_bridge_cache,
)
from ...models.jumpbridge import (
    JumpBridgeConfig,
    JumpBridgeNetwork,
    JumpBridgeImportRequest,
    JumpBridgeImportResponse,
)

router = APIRouter()


@router.get(
    "/",
    response_model=JumpBridgeConfig,
    summary="List all jump bridge networks",
    description="Returns all configured jump bridge networks and their bridges.",
)
def list_networks() -> JumpBridgeConfig:
    """Get all jump bridge networks."""
    return load_bridge_config()


@router.post(
    "/import",
    response_model=JumpBridgeImportResponse,
    summary="Import jump bridges",
    description="Import jump bridges from text format.",
)
def import_bridge_network(
    request: JumpBridgeImportRequest,
    replace: bool = Query(
        True,
        description="Replace existing network (true) or merge (false)",
    ),
) -> JumpBridgeImportResponse:
    """
    Import jump bridges from text format.

    Supported formats:
    - "System1 <-> System2" (bidirectional)
    - "System1 --> System2" (also bidirectional - bridges are always 2-way)
    - "System1 - System2" (simple format)

    Lines starting with # are ignored as comments.

    Example:
    ```
    # Delve bridges
    1DQ1-A <-> 8QT-H4
    49-U6U <-> PUIG-F
    ```
    """
    clear_bridge_cache()
    return import_bridges(
        network_name=request.network_name,
        bridge_text=request.bridge_text,
        replace=replace,
    )


@router.patch(
    "/{network_name}",
    summary="Toggle network status",
    description="Enable or disable a jump bridge network.",
)
def toggle_bridge_network(
    network_name: str,
    enabled: bool = Query(..., description="Enable or disable the network"),
) -> dict:
    """Enable or disable a jump bridge network."""
    clear_bridge_cache()
    if toggle_network(network_name, enabled):
        return {"status": "ok", "network": network_name, "enabled": enabled}
    raise HTTPException(status_code=404, detail=f"Network '{network_name}' not found")


@router.delete(
    "/{network_name}",
    summary="Delete a network",
    description="Delete a jump bridge network entirely.",
)
def delete_bridge_network(network_name: str) -> dict:
    """Delete a jump bridge network."""
    clear_bridge_cache()
    if delete_network(network_name):
        return {"status": "ok", "deleted": network_name}
    raise HTTPException(status_code=404, detail=f"Network '{network_name}' not found")


@router.get(
    "/{network_name}",
    response_model=JumpBridgeNetwork,
    summary="Get a specific network",
    description="Returns details for a specific jump bridge network.",
)
def get_network(network_name: str) -> JumpBridgeNetwork:
    """Get a specific jump bridge network."""
    config = load_bridge_config()
    for network in config.networks:
        if network.name == network_name:
            return network
    raise HTTPException(status_code=404, detail=f"Network '{network_name}' not found")
