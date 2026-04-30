from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_operator_or_admin
from app.core.config import settings
from app.models.ai_request_analysis import AIRequestAnalysis
from app.models.user import User
from app.schemas.ai_request_analysis import AIRequestAnalysisRead
from app.services.ai_service import analyze_administrative_request
from app.services.audit_service import create_audit_log
from app.services.request_service import get_request_or_404

router = APIRouter(prefix="/requests", tags=["ai analysis"])


@router.post("/{request_id}/ai-analysis", response_model=AIRequestAnalysisRead, status_code=201)
def create_ai_analysis(
    request_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> AIRequestAnalysis:
    request = get_request_or_404(db, request_id)
    analysis_data = analyze_administrative_request(request.description, request.request_type)
    analysis = AIRequestAnalysis(
        request_id=request.id,
        model_used=settings.openai_chat_model,
        **analysis_data,
    )
    db.add(analysis)
    request.priority = analysis.priority
    db.flush()
    create_audit_log(
        db,
        user_id=current_user.id,
        action="ai_analysis_created",
        entity_type="administrative_request",
        entity_id=request.id,
        new_value=analysis_data,
    )
    db.commit()
    db.refresh(analysis)
    return analysis
