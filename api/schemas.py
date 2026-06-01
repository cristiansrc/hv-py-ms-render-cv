from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class SupportedLanguage(str, Enum):
    ENGLISH = "english"
    SPANISH = "spanish"
    FRENCH = "french"
    GERMAN = "german"
    ITALIAN = "italian"
    PORTUGUESE = "portuguese"
    DUTCH = "dutch"
    DANISH = "danish"
    RUSSIAN = "russian"
    TURKISH = "turkish"
    HINDI = "hindi"
    INDONESIAN = "indonesian"
    JAPANESE = "japanese"
    KOREAN = "korean"
    MANDARIN_CHINESE = "mandarin_chinese"


class SupportedTheme(str, Enum):
    ENGINEERINGCLASSIC = "engineeringclassic"
    ENGINEERINGRESUMES = "engineeringresumes"
    MODERNCV = "moderncv"
    SB2NOV = "sb2nov"


class SocialNetwork(BaseModel):
    model_config = ConfigDict(extra="forbid")

    network: str = Field(..., min_length=1, max_length=50)
    username: str = Field(..., min_length=1, max_length=100)


class Locale(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: SupportedLanguage


class Design(BaseModel):
    model_config = ConfigDict(extra="forbid")

    theme: SupportedTheme


class CvData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Required fields
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr = Field(..., max_length=254)
    sections: dict[str, Any] = Field(..., min_length=1)

    # Optional fields
    phone: str | None = Field(default=None, max_length=30)
    location: str | None = Field(default=None, max_length=200)
    headline: str | None = Field(default=None, max_length=200)
    photo: str | None = Field(default=None, max_length=2048)
    website: HttpUrl | None = Field(default=None, max_length=2048)
    social_networks: list[SocialNetwork] | None = Field(default=None, max_length=20)
    locale: Locale | None = None
    design: Design | None = None


class RenderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cv: CvData


class RenderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pdf_base64: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str  # "healthy" or "unhealthy"
    timestamp: datetime
    version: str


class ApiErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str | None = None
    code: str
    message: str
    rejected_value: Any | None = None


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    status: int = Field(..., ge=400, le=599)
    error: str
    code: str
    message: str
    path: str
    trace_id: UUID
    details: list[ApiErrorDetail] = Field(default_factory=list)
