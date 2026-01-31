"""Company schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class CompanyBase(BaseModel):
    """Base schema for Company."""

    code: str = Field(..., min_length=2, max_length=20, description="회사 코드")
    name_ja: str = Field(..., min_length=1, max_length=100, description="일본어 회사명")
    name_en: str = Field(..., min_length=1, max_length=100, description="영어 회사명")
    name_ko: str | None = Field(None, max_length=100, description="한국어 회사명")
    website_url: HttpUrl = Field(..., description="공식 웹사이트 URL")
    price_page_url: HttpUrl = Field(..., description="요금 정보 페이지 URL")
    region: str | None = Field(None, max_length=100, description="관할 지역")
    description: str | None = Field(None, description="설명")


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""

    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    name_ja: str | None = Field(None, min_length=1, max_length=100)
    name_en: str | None = Field(None, min_length=1, max_length=100)
    name_ko: str | None = Field(None, max_length=100)
    website_url: HttpUrl | None = None
    price_page_url: HttpUrl | None = None
    region: str | None = Field(None, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class CompanyResponse(CompanyBase):
    """Schema for company response."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    plans_count: int = Field(default=0, description="등록된 요금제 수")

    model_config = {"from_attributes": True}


class CompanyListResponse(BaseModel):
    """Schema for company list response."""

    items: list[CompanyResponse]
    total: int
    page: int = 1
    page_size: int = 20
