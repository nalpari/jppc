# Investigation Report: Crawl Now Button Not Executing Crawl

## Bug Summary

**Issue**: 사용자가 Docker 기동 후 관리페이지에서 "Crawl Now" 버튼을 클릭해도 데이터가 크롤링되지 않음.

**Severity**: Critical - 핵심 기능 미작동

---

## Root Cause Analysis

### Primary Issue: Crawling Logic Commented Out

**Location**: `backend/app/api/v1/crawling.py:66-67`

```python
# TODO: Start actual crawling in background
# background_tasks.add_task(run_crawl, crawl_log.id, [c.id for c in companies])
```

**Problem**: `/api/v1/crawling/start` 엔드포인트에서 실제 크롤링 로직이 **주석 처리**되어 있음.

**Current Behavior**:
1. 프론트엔드에서 `POST /api/v1/crawling/start` 호출
2. 백엔드에서 `CrawlLog` 레코드 생성 (status: "pending")
3. **실제 크롤링 실행 없이** 응답 반환
4. 데이터베이스에 가격 데이터 저장되지 않음

**Expected Behavior**:
1. 프론트엔드에서 `POST /api/v1/crawling/start` 호출
2. 백엔드에서 `CrawlLog` 레코드 생성
3. `CrawlService.start_crawl()` 호출하여 백그라운드에서 크롤링 실행
4. 크롤링 결과를 `PricePlan`, `PriceHistory` 테이블에 저장
5. `CrawlLog` 상태를 "success" 또는 "failed"로 업데이트

---

## Affected Components

### Backend
- `backend/app/api/v1/crawling.py` - API 엔드포인트 (버그 위치)
- `backend/app/services/crawl_service.py` - 크롤링 서비스 (구현 완료됨)
- `backend/app/crawlers/` - 각 전력회사별 크롤러 (구현 완료됨)

### Frontend
- `frontend/src/app/crawling/page.tsx` - Crawling 관리 페이지
- `frontend/src/lib/api.ts` - API 클라이언트

### Data Flow
```
Frontend (Start Crawl button)
    ↓
POST /api/v1/crawling/start
    ↓
start_crawl() in crawling.py
    ↓
[BLOCKED] background_tasks.add_task() - 주석 처리됨
    ↓
CrawlService.start_crawl() - 호출되지 않음
    ↓
Crawlers (tepco, chubu, kepco, chugoku) - 실행되지 않음
    ↓
Database (PricePlan, PriceHistory) - 데이터 저장 안됨
```

---

## Proposed Solution

### Option 1: Integrate CrawlService (Recommended)

`crawling.py`의 `start_crawl` 함수를 수정하여 `CrawlService`를 사용:

1. `crawl_service` 인스턴스를 import
2. `background_tasks.add_task()`를 활성화하고 `CrawlService.start_crawl()` 호출
3. 크롤링 상태 추적을 위해 `_crawl_state` 업데이트 로직 추가

**Key Changes**:
```python
from app.services.crawl_service import crawl_service

async def run_crawl(crawl_log_id: int, company_ids: list[int], db_session_factory):
    async with db_session_factory() as db:
        # Convert company IDs to codes
        companies = await db.execute(
            select(Company).where(Company.id.in_(company_ids))
        )
        company_codes = [c.code for c in companies.scalars().all()]

        # Start crawl using service
        await crawl_service.start_crawl(db, company_codes=company_codes)
```

### Option 2: Direct Crawler Invocation

API 엔드포인트에서 직접 크롤러를 호출하는 방식.

**Pros**: 간단한 구현
**Cons**: `CrawlService`의 기능(job tracking, callbacks 등) 미사용

---

## Edge Cases & Potential Side Effects

1. **동시 크롤링 방지**: 현재 `_crawl_state["is_running"]` 체크가 있지만, `CrawlService`와 동기화 필요
2. **DB 세션 관리**: 백그라운드 태스크에서 별도의 DB 세션 생성 필요
3. **에러 핸들링**: 크롤링 실패 시 `CrawlLog` 상태 업데이트 필요
4. **메모리 관리**: 장시간 실행되는 크롤링 작업의 리소스 관리

---

## Additional Observations

### Existing Crawlers (Implemented)
- `tepco_crawler.py` - 東京電力
- `chubu_crawler.py` - 中部電力
- `kepco_crawler.py` - 関西電力
- `chugoku_crawler.py` - 中国電力

### CrawlService Features (Implemented)
- Job management (`CrawlJob` class)
- Parallel crawler execution
- Price plan saving with change detection
- Price history tracking
- Crawl logging

### Frontend Features (Implemented)
- Manual crawl trigger (`handleStartCrawl`)
- Crawl status polling
- Log viewing with pagination
- Schedule configuration

---

## Implementation Notes

### Changes Made

**File**: `backend/app/api/v1/crawling.py`

1. **Added imports**:
   - `async_session_maker` from `app.db.database`
   - `crawl_service` from `app.services.crawl_service`
   - `get_logger` from `app.utils.logger`

2. **Added `run_crawl_task` function** (lines 35-130):
   - Background task that executes crawling via `CrawlService`
   - Updates `_crawl_state` for real-time progress tracking
   - Handles crawl log status updates (running → success/failed/partial)
   - Includes error handling with proper cleanup

3. **Modified `start_crawl` endpoint** (lines 167-171):
   - Extracts company codes from companies
   - Calls `background_tasks.add_task(run_crawl_task, crawl_log.id, company_codes)`

4. **Modified `stop_crawl` endpoint** (lines 181-211):
   - Cancels active jobs in `CrawlService`
   - Updates crawl log status to "cancelled"

### Test Results

- **Syntax check**: PASSED (`python -m py_compile`)
- **Import test**: Could not run (FastAPI not installed in test environment)
- **Docker environment**: Not tested locally

### How to Verify the Fix

1. Rebuild and restart Docker containers:
   ```bash
   docker-compose build backend
   docker-compose up -d
   ```

2. Navigate to the Crawling Management page

3. Click "Start Crawl" button

4. Expected behavior:
   - Status should change to "Running"
   - Progress bar should update
   - After completion, logs should show crawl results
   - Price data should appear in the Prices page
