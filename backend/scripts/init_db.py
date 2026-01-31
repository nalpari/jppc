"""Initialize database with tables and seed data."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.database import engine, async_session_maker, Base
from app.models import Company, AlertSetting


SEED_COMPANIES = [
    {
        "code": "tepco",
        "name_ja": "東京電力エナジーパートナー",
        "name_en": "TEPCO Energy Partner",
        "name_ko": "도쿄전력 에너지파트너",
        "website_url": "https://www.tepco.co.jp/",
        "price_page_url": "https://www.tepco.co.jp/ep/private/plan/index-j.html",
        "region": "関東",
        "description": "関東地方を中心に電力を供給する大手電力会社",
        "is_active": True,
    },
    {
        "code": "chubu",
        "name_ja": "中部電力ミライズ",
        "name_en": "Chubu Electric Power Miraiz",
        "name_ko": "주부전력 미라이즈",
        "website_url": "https://www.chuden.co.jp/",
        "price_page_url": "https://miraiz.chuden.co.jp/home/electric/menu/",
        "region": "中部",
        "description": "中部地方を中心に電力を供給する大手電力会社",
        "is_active": True,
    },
    {
        "code": "kepco",
        "name_ja": "関西電力",
        "name_en": "Kansai Electric Power",
        "name_ko": "간사이전력",
        "website_url": "https://www.kepco.co.jp/",
        "price_page_url": "https://kepco.jp/ryokin/menu/",
        "region": "関西",
        "description": "関西地方を中心に電力を供給する大手電力会社",
        "is_active": True,
    },
    {
        "code": "chugoku",
        "name_ja": "中国電力",
        "name_en": "Chugoku Electric Power",
        "name_ko": "주고쿠전력",
        "website_url": "https://www.energia.co.jp/",
        "price_page_url": "https://www.energia.co.jp/elec/price/",
        "region": "中国",
        "description": "中国地方を中心に電力を供給する大手電力会社",
        "is_active": True,
    },
]

SEED_ALERT_SETTINGS = [
    {
        "alert_type": "price_change",
        "is_enabled": True,
    },
    {
        "alert_type": "crawl_failure",
        "is_enabled": True,
    },
    {
        "alert_type": "weekly_report",
        "is_enabled": False,
    },
]


async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created successfully")


async def seed_companies():
    """Seed companies data."""
    print("Seeding companies...")
    async with async_session_maker() as db:
        # Check if companies already exist
        result = await db.execute(text("SELECT COUNT(*) FROM companies"))
        count = result.scalar()

        if count > 0:
            print(f"  Companies already exist ({count} records), skipping...")
            return

        for company_data in SEED_COMPANIES:
            company = Company(**company_data)
            db.add(company)

        await db.commit()
        print(f"✓ Seeded {len(SEED_COMPANIES)} companies")


async def seed_alert_settings():
    """Seed alert settings."""
    print("Seeding alert settings...")
    async with async_session_maker() as db:
        # Check if alert settings already exist
        result = await db.execute(text("SELECT COUNT(*) FROM alert_settings"))
        count = result.scalar()

        if count > 0:
            print(f"  Alert settings already exist ({count} records), skipping...")
            return

        for alert_data in SEED_ALERT_SETTINGS:
            alert = AlertSetting(**alert_data)
            db.add(alert)

        await db.commit()
        print(f"✓ Seeded {len(SEED_ALERT_SETTINGS)} alert settings")


async def main():
    """Main initialization function."""
    print("=" * 50)
    print("Database Initialization")
    print("=" * 50)

    try:
        await create_tables()
        await seed_companies()
        await seed_alert_settings()

        print("=" * 50)
        print("✓ Database initialization complete!")
        print("=" * 50)

    except Exception as e:
        print(f"✗ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
