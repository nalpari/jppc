"""Companies API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from app.api.deps import DbSession
from app.models import Company, PricePlan
from app.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
)

router = APIRouter()


@router.get("", response_model=CompanyListResponse)
async def list_companies(
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: bool | None = None,
):
    """전력회사 목록 조회."""
    query = select(Company)

    if is_active is not None:
        query = query.where(Company.is_active == is_active)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Get paginated results
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    companies = result.scalars().all()

    # Get plans count for each company
    items = []
    for company in companies:
        plans_count_query = select(func.count()).where(
            PricePlan.company_id == company.id
        )
        plans_count = await db.scalar(plans_count_query) or 0

        company_dict = {
            **company.__dict__,
            "plans_count": plans_count,
        }
        items.append(CompanyResponse.model_validate(company_dict))

    return CompanyListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(db: DbSession, company_id: int):
    """전력회사 상세 조회."""
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get plans count
    plans_count_query = select(func.count()).where(PricePlan.company_id == company_id)
    plans_count = await db.scalar(plans_count_query) or 0

    company_dict = {**company.__dict__, "plans_count": plans_count}
    return CompanyResponse.model_validate(company_dict)


@router.post("", response_model=CompanyResponse, status_code=201)
async def create_company(db: DbSession, data: CompanyCreate):
    """전력회사 등록."""
    # Check for duplicate code
    existing = await db.scalar(select(Company).where(Company.code == data.code))
    if existing:
        raise HTTPException(status_code=400, detail="Company code already exists")

    company = Company(
        code=data.code,
        name_ja=data.name_ja,
        name_en=data.name_en,
        name_ko=data.name_ko,
        website_url=str(data.website_url),
        price_page_url=str(data.price_page_url),
        region=data.region,
        description=data.description,
    )
    db.add(company)
    await db.flush()
    await db.refresh(company)

    company_dict = {**company.__dict__, "plans_count": 0}
    return CompanyResponse.model_validate(company_dict)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(db: DbSession, company_id: int, data: CompanyUpdate):
    """전력회사 정보 수정."""
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ("website_url", "price_page_url") and value is not None:
            value = str(value)
        setattr(company, field, value)

    await db.flush()
    await db.refresh(company)

    plans_count_query = select(func.count()).where(PricePlan.company_id == company_id)
    plans_count = await db.scalar(plans_count_query) or 0

    company_dict = {**company.__dict__, "plans_count": plans_count}
    return CompanyResponse.model_validate(company_dict)


@router.delete("/{company_id}", status_code=204)
async def delete_company(db: DbSession, company_id: int):
    """전력회사 삭제."""
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    await db.delete(company)
