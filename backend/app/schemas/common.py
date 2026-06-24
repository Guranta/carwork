from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Pagination(BaseModel):
    total: int
    page: int
    page_size: int


class HealthOut(BaseModel):
    status: str
    app: str
    env: str
    version: str
    timestamp: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(ORMBase):
    id: int
    name: str
    phone: str | None = None
    role: str
    is_active: bool


class VehicleIn(BaseModel):
    vin: str
    plate_no: str | None = None
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None


class VehicleOut(ORMBase):
    id: int
    vin: str
    plate_no: str | None = None
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None


class DocumentOut(ORMBase):
    id: int
    type: str
    object_key: str
    status: str
    confidence: float | None = None
    extracted: dict | None = None


class OCRExtractOut(BaseModel):
    document_id: int
    doc_type: str
    extracted: dict
    confidence: float
    status: str


class DamageAssessmentIn(BaseModel):
    image_urls: list[str]
    vehicle_info: dict | None = None


class ChatIn(BaseModel):
    query: str
    history: list[dict] | None = None


class ChatOut(BaseModel):
    answer: str
    provider: str
    model: str | None = None


class ClaimCaseIn(BaseModel):
    insurance_policy_no: str | None = None
    insurance_company: str | None = None
    vin: str
    incident_at: str | None = None
    incident_location: str | None = None
    description: str | None = None


class ClaimCaseOut(ORMBase):
    id: int
    case_no: str
    status: str
    stage: str | None = None
    estimated_amount: float | None = None
    service_order_no: str | None = None


class ServiceOrderIn(BaseModel):
    vin: str | None = None
    fault_desc: str | None = None
    items: list[dict] | None = None


class ServiceOrderOut(ORMBase):
    id: int
    order_no: str
    status: str
    fault_desc: str | None = None
    total_amount: float | None = None
