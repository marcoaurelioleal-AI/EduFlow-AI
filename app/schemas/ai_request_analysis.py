from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import Priority, RequestType, RiskLevel


class AIRequestAnalysisRead(BaseModel):
    id: int
    request_id: int
    predicted_category: RequestType
    priority: Priority
    summary: str
    suggested_action: str
    risk_level: RiskLevel
    model_used: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
