# ⚡ Japan Power Price Crawler (JPPC)

일본 주요 4개 전력회사(도쿄전력, 츄부전력, 칸사이전력, 츄고쿠전력)의 전기 요금 정보를 자동으로 수집하고 비교 분석하는 시스템입니다.

---

## 📋 주요 기능

- **자동 요금 수집**: 도쿄전력(TEPCO), 츄부전력, 칸사이전력(KEPCO), 츄고쿠전력의 요금 정보를 자동으로 크롤링
- **요금 비교**: 여러 전력회사의 요금을 사용량 기반으로 비교 분석
- **변동 추적**: 요금 변경 이력을 추적하고 시각화
- **알림 시스템**: 크롤링 실패, 요금 변경 시 이메일 알림
- **스케줄링**: 주 1회 자동 크롤링 스케줄 설정

---

## 🛠 기술 스택

### Backend
- **Python 3.12+** - 메인 언어
- **FastAPI** - 비동기 REST API
- **Playwright** - 웹 크롤링
- **SQLAlchemy 2.0** - 비동기 ORM
- **PostgreSQL 16** - 데이터베이스
- **APScheduler** - 작업 스케줄링
- **aiosmtplib** - 이메일 발송

### Frontend
- **Next.js 14+** - React 프레임워크
- **TypeScript** - 타입 안전성
- **TailwindCSS** - 스타일링
- **React Query** - 서버 상태 관리
- **Recharts** - 차트 라이브러리

### Infrastructure
- **Docker & Docker Compose** - 컨테이너화
- **Nginx** - 리버스 프록시

---

## 🚀 빠른 시작

### 요구 사항

- Docker 24.0+
- Docker Compose 2.20+
- Git

### 설치 및 실행

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-repo/jppc.git
cd jppc

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정

# 3. 서비스 시작
docker compose up -d

# 4. 로그 확인
docker compose logs -f
```

### 접속 URL

| 서비스 | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

---

## 📁 프로젝트 구조

```
jppc/
├── backend/                # Backend 서비스
│   ├── app/
│   │   ├── api/           # API 엔드포인트
│   │   ├── crawlers/      # 전력회사별 크롤러
│   │   ├── models/        # SQLAlchemy 모델
│   │   ├── schemas/       # Pydantic 스키마
│   │   ├── services/      # 비즈니스 로직
│   │   └── templates/     # 이메일 템플릿
│   ├── alembic/           # DB 마이그레이션
│   └── tests/             # 테스트 코드
│
├── frontend/              # Frontend 서비스
│   ├── src/
│   │   ├── app/          # Next.js App Router 페이지
│   │   ├── components/   # React 컴포넌트
│   │   ├── hooks/        # React Query 커스텀 훅
│   │   └── lib/          # API 클라이언트 및 유틸리티
│   └── public/
│
├── nginx/                 # Nginx 설정
├── docs/                  # 문서
│   ├── PRD.md            # 요구사항 정의서
│   ├── PLAN.md           # 구현 계획서
│   ├── api-spec.md       # API 명세서
│   ├── database-schema.md # DB 스키마
│   └── deployment.md     # 배포 가이드
│
├── docker-compose.yml     # 개발 환경
├── docker-compose.prod.yml # 프로덕션 환경
└── .env.example           # 환경 변수 템플릿
```

---

## 📊 지원 전력회사

| 회사 | 코드 | 지역 | 웹사이트 |
|------|------|------|----------|
| 도쿄전력 (TEPCO) | tepco | 관동 | https://www.tepco.co.jp |
| 츄부전력 | chubu | 중부 | https://www.chuden.co.jp |
| 칸사이전력 (KEPCO) | kepco | 관서 | https://www.kepco.co.jp |
| 츄고쿠전력 | chugoku | 중국 | https://www.energia.co.jp |

---

## 📖 API 개요

### 주요 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/companies` | 전력회사 목록 |
| GET | `/api/v1/prices` | 요금 정보 목록 |
| POST | `/api/v1/prices/compare` | 요금 비교 |
| POST | `/api/v1/crawling/start` | 크롤링 시작 |
| GET | `/api/v1/crawling/status` | 크롤링 상태 |
| GET | `/api/v1/stats/dashboard` | 대시보드 통계 |

자세한 API 명세는 [API 문서](docs/api-spec.md)를 참조하세요.

---

## ⚙️ 환경 변수

### 필수 설정

```bash
# 데이터베이스
DB_USER=jppc
DB_PASSWORD=your_password
DB_NAME=jppc

# 보안
SECRET_KEY=your_secret_key
```

### 선택 설정

```bash
# 이메일 알림 (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_app_password

# CORS
CORS_ORIGINS=http://localhost:3000
```

---

## 🧪 테스트

```bash
# Backend 테스트
docker compose exec backend pytest

# 커버리지 포함
docker compose exec backend pytest --cov=app

# E2E 테스트
docker compose exec backend pytest tests/test_e2e/
```

---

## 🚢 프로덕션 배포

```bash
# 프로덕션 환경 변수 설정
cp .env.example .env.prod
# .env.prod 편집

# 프로덕션 빌드 및 실행
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

자세한 배포 가이드는 [배포 문서](docs/deployment.md)를 참조하세요.

---

## 📝 문서

| 문서 | 설명 |
|------|------|
| [PRD.md](docs/PRD.md) | 요구사항 정의서 |
| [PLAN.md](docs/PLAN.md) | 구현 계획서 |
| [api-spec.md](docs/api-spec.md) | API 명세서 |
| [database-schema.md](docs/database-schema.md) | 데이터베이스 스키마 |
| [deployment.md](docs/deployment.md) | 배포 가이드 |

---

## 📝 라이선스

MIT License

---

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

_마지막 업데이트: 2026-01-31_
