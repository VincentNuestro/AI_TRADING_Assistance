from __future__ import annotations

from fastapi import APIRouter, Response

router = APIRouter(tags=["metrics"])


@router.get("/metrics", summary="Prometheus metrics")
async def metrics() -> Response:
    # Placeholder for Prometheus metrics export
    return Response("# HELP app_info Application info\n# TYPE app_info gauge\napp_info 1", media_type="text/plain")
