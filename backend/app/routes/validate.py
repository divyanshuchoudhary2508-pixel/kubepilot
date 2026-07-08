from fastapi import APIRouter

from app.schemas.manifest import ManifestRequest, ValidationResponse
from app.validators.engine import run_validation

router = APIRouter()


@router.post("/validate", response_model=ValidationResponse)
def validate_manifest(request: ManifestRequest) -> ValidationResponse:
    """Run the full rule set against the submitted YAML and return the report."""
    return run_validation(request.content)
