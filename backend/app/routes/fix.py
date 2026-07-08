from fastapi import APIRouter

from app.schemas.manifest import FixResponse, ManifestRequest
from app.validators.fixers import apply_fixes

router = APIRouter()


@router.post("/fix", response_model=FixResponse)
def fix_manifest(request: ManifestRequest) -> FixResponse:
    """Apply deterministic, mechanical fixes and return the patched YAML."""
    fixed_content, applied_fixes = apply_fixes(request.content)
    return FixResponse(fixed_content=fixed_content, applied_fixes=applied_fixes)
