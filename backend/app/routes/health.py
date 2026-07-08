from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Simple liveness check for uptime monitors / Render health checks."""
    return {"status": "ok"}
