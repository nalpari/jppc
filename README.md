# ⚡ Japan Power Price Crawler (JPPC)

일본 주요 4개 전력회사(도쿄전력, 츄부전력, 칸사이전력, 츄고쿠전력)의 전기 요금 정보를 자동으로 수집하고 비교 분석하는 시스템입니다.

---

## 📋 주요 기능

- **자동 요금 수집**: 도쿄전력(TEPCO), 츄부전력, 칸사이전력(KEPCO), 츄고쿠전력의 요금 정보를 자동으로 크롤링
- **요금 비교**: 여러 전력회사의 요금을 사용량 기반으로 비교 분석
- **변동 추적**: 요금 변경 이력을 추적하고 시각화
- **알림 시스템**: 크롤링 실패, 요금 변경 시 이메일 알림
- **대시보드**: 전체 현황 요약 및 통계 시각화

---

## 🛠 기술 스택

### Backend
- **Python 3.12+** - 메인 언어
- **FastAPI 0.109+** - 비동기 REST API
- **Playwright 1.41+** - 웹 크롤링
- **SQLAlchemy 2.0+** - 비동기 ORM (asyncpg)
- **PostgreSQL 16** - 데이터베이스
- **Alembic** - DB 마이그레이션
- **Pydantic 2.6+** - 데이터 검증
- **aiosmtplib** - 비동기 이메일 발송
- **Tenacity** - 재시도 로직

### Frontend
- **Next.js 14.1+** - React 프레임워크 (App Router)
- **TypeScript 5.9+** - 타입 안전성
- **TailwindCSS 3.4+** - 스타일링
- **Radix UI** - 접근성 기반 UI 컴포넌트
- **TanStack Query 5.20+** - 서버 상태 관리
- **Recharts 2.12+** - 차트 라이브러리
- **Axios** - HTTP 클라이언트

### Infrastructure
- **Docker & Docker Compose** - 컨테이너화
- **Nginx** - 리버스 프록시 (프로덕션)

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

### 접속 URL (개발 환경)

| 서비스 | URL |
|--------|-----|
| Frontend | http://localhost:3001 |
| Backend API | http://localhost:8080 |
| API Docs (Swagger) | http://localhost:8080/docs |
| API Docs (ReDoc) | http://localhost:8080/redoc |
| PostgreSQL | localhost:5432 |

---

## 📁 프로젝트 구조

```
jppc/
├── backend/                  # Backend 서비스
│   ├── app/
│   │   ├── api/v1/          # REST API 엔드포인트
│   │   ├── crawlers/        # 전력회사별 Playwright 크롤러
│   │   ├── db/              # 데이터베이스 유틸리티
│   │   │   └── repositories/ # Repository 패턴 구현
│   │   ├── models/          # SQLAlchemy ORM 모델
│   │   ├── schemas/         # Pydantic 요청/응답 스키마
│   │   ├── services/        # 비즈니스 로직 레이어
│   │   ├── templates/email/ # 이메일 알림 템플릿
│   │   ├── utils/           # 로깅 및 헬퍼 유틸리티
│   │   ├── config.py        # Pydantic 설정 관리
│   │   └── main.py          # FastAPI 엔트리포인트
│   ├── alembic/             # DB 마이그레이션
│   ├── tests/               # pytest 테스트
│   ├── pyproject.toml       # Python 프로젝트 설정
│   └── Dockerfile           # 멀티스테이지 Docker 빌드
│
├── frontend/                # Frontend 서비스
│   ├── src/
│   │   ├── app/            # Next.js App Router 페이지
│   │   ├── components/     # React 컴포넌트 (도메인별 구성)
│   │   │   └── ui/         # Radix UI 기반 공통 컴포넌트
│   │   ├── hooks/          # React Query 커스텀 훅
│   │   ├── lib/            # API 클라이언트 및 유틸리티
│   │   └── types/          # TypeScript 타입 정의
│   ├── public/
│   └── Dockerfile          # 멀티스테이지 Docker 빌드
│
├── nginx/                   # Nginx 리버스 프록시 설정
├── docs/                    # 프로젝트 문서
├── docker-compose.yml       # 개발 환경
├── docker-compose.prod.yml  # 프로덕션 환경
└── .env.example             # 환경 변수 템플릿
```

---

## 📊 지원 전력회사

| 회사 | 일본어명 | 코드 | 지역 | 크롤링 URL |
|------|----------|------|------|-----------|
| 도쿄전력 | 東京電力 (TEPCO) | tepco | 관동 | https://www.tepco.co.jp/ |
| 츄부전력 | 中部電力 | chubu | 중부 | https://miraiz.chuden.co.jp/ |
| 칸사이전력 | 関西電力 (KEPCO) | kepco | 관서 | https://kepco.jp/ |
| 츄고쿠전력 | 中国電力 | chugoku | 중국 | https://www.energia-support.com/ |

---

## 📖 API 개요

### 주요 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/companies` | 전력회사 목록 |
| GET | `/api/v1/companies/{id}` | 전력회사 상세 |
| GET | `/api/v1/prices` | 요금 정보 목록 |
| GET | `/api/v1/prices/{id}` | 요금 상세 |
| POST | `/api/v1/prices/compare` | 요금 비교 |
| POST | `/api/v1/crawling/start` | 크롤링 시작 |
| GET | `/api/v1/crawling/status` | 크롤링 상태 |
| GET | `/api/v1/crawling/logs` | 크롤링 이력 |
| GET | `/api/v1/stats/dashboard` | 대시보드 통계 |
| GET | `/api/v1/alerts` | 알림 설정 조회 |
| POST | `/api/v1/alerts` | 알림 설정 생성 |

자세한 API 명세는 [API 문서](docs/api-spec.md) 또는 http://localhost:8080/docs (Swagger UI)를 참조하세요.

---

## ⚙️ 환경 변수

### 데이터베이스 설정

```bash
POSTGRES_USER=jppc
POSTGRES_PASSWORD=jppc_password
POSTGRES_DB=jppc_db
```

### Backend 설정

```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 이메일 알림 (SMTP) - 선택

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@jppc.local
```

### Frontend 설정

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

---

## 🧪 테스트

```bash
# Backend 테스트
docker compose exec backend pytest

# 커버리지 포함
docker compose exec backend pytest --cov=app

# 특정 테스트 파일 실행
docker compose exec backend pytest tests/test_api/test_companies.py

# E2E 테스트
docker compose exec backend pytest tests/test_e2e/
```

---

## 🔧 개발 도구

### Backend 코드 품질

```bash
# 타입 체크
docker compose exec backend mypy app

# 린트
docker compose exec backend ruff check app

# 포매팅
docker compose exec backend black app

# 린트 자동 수정
docker compose exec backend ruff check app --fix
```

### Frontend 코드 품질

```bash
# 린트
docker compose exec frontend npm run lint

# 타입 체크
docker compose exec frontend npm run type-check
```

### 데이터베이스 마이그레이션

```bash
# 마이그레이션 적용
docker compose exec backend alembic upgrade head

# 새 마이그레이션 생성
docker compose exec backend alembic revision --autogenerate -m "설명"

# 마이그레이션 롤백
docker compose exec backend alembic downgrade -1
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
