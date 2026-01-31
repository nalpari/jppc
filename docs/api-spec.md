# 📖 API 명세서 - Japan Power Price Crawler (JPPC)

> API Version: v1
> Base URL: `http://localhost:8000/api/v1`
> OpenAPI Docs: `http://localhost:8000/docs`

---

## 📋 목차

1. [인증](#인증)
2. [공통 응답 형식](#공통-응답-형식)
3. [Companies API](#companies-api)
4. [Prices API](#prices-api)
5. [Crawling API](#crawling-api)
6. [Alerts API](#alerts-api)
7. [Stats API](#stats-api)
8. [Health API](#health-api)

---

## 인증

현재 버전에서는 인증이 필요하지 않습니다.
향후 API Key 또는 JWT 기반 인증이 추가될 예정입니다.

---

## 공통 응답 형식

### 성공 응답

```json
{
  "data": { ... },
  "message": "Success"
}
```

### 페이지네이션 응답

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

### 에러 응답

```json
{
  "detail": "Error message description"
}
```

### HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 201 | 생성됨 |
| 204 | 삭제됨 (No Content) |
| 400 | 잘못된 요청 |
| 404 | 리소스 없음 |
| 422 | 유효성 검증 실패 |
| 500 | 서버 오류 |

---

## Companies API

### 전력회사 목록 조회

```http
GET /api/v1/companies
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| page | int | No | 페이지 번호 (기본값: 1) |
| page_size | int | No | 페이지 크기 (기본값: 20, 최대: 100) |
| is_active | bool | No | 활성화 상태 필터 |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "code": "tepco",
      "name_ja": "東京電力",
      "name_en": "Tokyo Electric Power Company",
      "name_ko": "도쿄전력",
      "website_url": "https://www.tepco.co.jp",
      "price_page_url": "https://www.tepco.co.jp/ep/private/plan/",
      "region": "Kanto",
      "is_active": true,
      "created_at": "2026-01-31T10:00:00Z",
      "updated_at": "2026-01-31T10:00:00Z"
    }
  ],
  "total": 4,
  "page": 1,
  "page_size": 20
}
```

### 전력회사 상세 조회

```http
GET /api/v1/companies/{id}
```

**Path Parameters:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| id | int | 회사 ID |

### 전력회사 등록

```http
POST /api/v1/companies
```

**Request Body:**

```json
{
  "code": "tepco",
  "name_ja": "東京電力",
  "name_en": "Tokyo Electric Power Company",
  "name_ko": "도쿄전력",
  "website_url": "https://www.tepco.co.jp",
  "price_page_url": "https://www.tepco.co.jp/ep/private/plan/",
  "region": "Kanto"
}
```

### 전력회사 수정

```http
PATCH /api/v1/companies/{id}
```

**Request Body:** (수정할 필드만 포함)

```json
{
  "name_ko": "동경전력",
  "is_active": false
}
```

### 전력회사 삭제

```http
DELETE /api/v1/companies/{id}
```

---

## Prices API

### 요금 목록 조회

```http
GET /api/v1/prices
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| page | int | No | 페이지 번호 |
| page_size | int | No | 페이지 크기 |
| company_id | int | No | 회사 ID 필터 |
| plan_type | string | No | 요금제 타입 필터 (residential, commercial) |
| is_current | bool | No | 현재 요금만 필터 |

### 요금 상세 조회

```http
GET /api/v1/prices/{id}
```

**Response:**

```json
{
  "id": 1,
  "company_id": 1,
  "plan_code": "従量電灯B",
  "plan_name_ja": "従量電灯B",
  "plan_name_en": "Metered Lighting B",
  "plan_type": "residential",
  "base_charge": 858.00,
  "tier1_limit": 120,
  "tier1_price": 19.88,
  "tier2_limit": 300,
  "tier2_price": 26.48,
  "tier3_price": 30.57,
  "fuel_adjustment": 1.23,
  "renewable_surcharge": 3.45,
  "effective_date": "2026-01-01",
  "is_current": true,
  "created_at": "2026-01-31T10:00:00Z"
}
```

### 요금 이력 조회

```http
GET /api/v1/prices/{id}/history
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| limit | int | No | 조회 개수 (기본값: 10) |

### 요금 비교

```http
POST /api/v1/prices/compare
```

**Request Body:**

```json
{
  "plan_ids": [1, 2, 3],
  "usage_kwh": 300
}
```

**Response:**

```json
{
  "comparisons": [
    {
      "plan_id": 1,
      "company_name": "東京電力",
      "plan_name": "従量電灯B",
      "base_charge": 858.00,
      "usage_charge": 7944.00,
      "fuel_adjustment": 369.00,
      "renewable_surcharge": 1035.00,
      "total_cost": 10206.00
    }
  ],
  "usage_kwh": 300
}
```

---

## Crawling API

### 크롤링 상태 조회

```http
GET /api/v1/crawling/status
```

**Response:**

```json
{
  "is_running": false,
  "current_job": null,
  "last_run": "2026-01-30T03:00:00Z",
  "next_scheduled_run": "2026-02-06T03:00:00Z"
}
```

### 크롤링 시작

```http
POST /api/v1/crawling/start
```

**Request Body:**

```json
{
  "company_ids": [1, 2],
  "force": false
}
```

- `company_ids`: 생략하면 모든 활성 회사 대상
- `force`: true면 캐시 무시하고 강제 실행

**Response:**

```json
{
  "job_id": "crawl_20260131_120000",
  "status": "started",
  "companies": ["tepco", "chubu"]
}
```

### 크롤링 중지

```http
POST /api/v1/crawling/stop
```

### 크롤링 로그 조회

```http
GET /api/v1/crawling/logs
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| page | int | No | 페이지 번호 |
| page_size | int | No | 페이지 크기 |
| company_id | int | No | 회사 ID 필터 |
| status | string | No | 상태 필터 (success, failed, running) |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "company_id": 1,
      "company_name": "東京電力",
      "status": "success",
      "plans_found": 5,
      "prices_updated": 2,
      "duration_seconds": 45,
      "error_message": null,
      "started_at": "2026-01-31T03:00:00Z",
      "completed_at": "2026-01-31T03:00:45Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### 스케줄 조회

```http
GET /api/v1/crawling/schedule
```

**Response:**

```json
{
  "is_enabled": true,
  "day_of_week": 0,
  "hour": 3,
  "minute": 0,
  "timezone": "Asia/Tokyo"
}
```

### 스케줄 수정

```http
PUT /api/v1/crawling/schedule
```

**Request Body:**

```json
{
  "is_enabled": true,
  "day_of_week": 0,
  "hour": 3,
  "minute": 0
}
```

- `day_of_week`: 0=월요일, 6=일요일

---

## Alerts API

### 알림 설정 목록 조회

```http
GET /api/v1/alerts
```

**Response:**

```json
[
  {
    "id": 1,
    "alert_type": "crawl_failure",
    "is_enabled": true,
    "recipients": [
      {
        "id": 1,
        "email": "admin@example.com",
        "name": "Admin",
        "is_active": true
      }
    ]
  }
]
```

### 알림 설정 조회

```http
GET /api/v1/alerts/{alert_type}
```

**Alert Types:**

- `crawl_failure`: 크롤링 실패 알림
- `price_change`: 요금 변경 알림
- `weekly_report`: 주간 리포트

### 알림 설정 수정

```http
PATCH /api/v1/alerts/{alert_type}
```

**Request Body:**

```json
{
  "is_enabled": true
}
```

### 수신자 추가

```http
POST /api/v1/alerts/{alert_type}/recipients
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "name": "User Name"
}
```

### 수신자 삭제

```http
DELETE /api/v1/alerts/{alert_type}/recipients/{recipient_id}
```

---

## Stats API

### 대시보드 통계 조회

```http
GET /api/v1/stats/dashboard
```

**Response:**

```json
{
  "companies": {
    "total": 4,
    "active": 4
  },
  "price_plans": {
    "total": 16,
    "current": 16
  },
  "crawling": {
    "last_run": "2026-01-31T03:00:00Z",
    "success_rate": 100.0,
    "total_runs_30d": 4
  },
  "recent_changes": [
    {
      "company_name": "東京電力",
      "plan_name": "従量電灯B",
      "change_type": "price_update",
      "changed_at": "2026-01-30T03:00:00Z"
    }
  ]
}
```

### 회사별 통계 조회

```http
GET /api/v1/stats/companies/{company_id}
```

---

## Health API

### 헬스 체크

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "timestamp": "2026-01-31T12:00:00Z"
}
```

---

## 에러 코드

| 코드 | 메시지 | 설명 |
|------|--------|------|
| COMPANY_NOT_FOUND | Company not found | 회사를 찾을 수 없음 |
| COMPANY_ALREADY_EXISTS | Company code already exists | 중복된 회사 코드 |
| PRICE_NOT_FOUND | Price plan not found | 요금제를 찾을 수 없음 |
| CRAWL_ALREADY_RUNNING | Crawl job already running | 이미 크롤링 진행 중 |
| INVALID_SCHEDULE | Invalid schedule configuration | 잘못된 스케줄 설정 |
| ALERT_NOT_FOUND | Alert setting not found | 알림 설정을 찾을 수 없음 |

---

_문서 버전: 1.0_
_최종 수정: 2026-01-31_
