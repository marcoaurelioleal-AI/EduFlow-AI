from typing import Literal

StudentStatus = Literal["active", "inactive", "blocked", "graduated"]
EnrollmentStatus = Literal["pending", "active", "cancelled", "completed", "blocked"]
PaymentStatus = Literal["pending", "paid", "overdue", "refunded"]
RequestType = Literal[
    "enrollment_change",
    "discount_request",
    "refund_request",
    "document_request",
    "financial_review",
    "cancellation_request",
]
RequestStatus = Literal["pending", "in_review", "approved", "rejected", "completed"]
Priority = Literal["low", "medium", "high", "critical"]
RiskLevel = Literal["low", "medium", "high"]
UserRole = Literal["admin", "operator", "viewer"]
