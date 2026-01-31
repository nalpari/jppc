# 🚀 배포 가이드 - Japan Power Price Crawler (JPPC)

---

## 📋 목차

1. [요구 사항](#요구-사항)
2. [개발 환경 설정](#개발-환경-설정)
3. [프로덕션 배포](#프로덕션-배포)
4. [환경 변수](#환경-변수)
5. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
6. [모니터링](#모니터링)
7. [백업 및 복원](#백업-및-복원)
8. [트러블슈팅](#트러블슈팅)

---

## 요구 사항

### 시스템 요구 사항

| 항목 | 최소 | 권장 |
|------|------|------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Storage | 20 GB | 50 GB |
| OS | Ubuntu 20.04+ / Debian 11+ | Ubuntu 22.04 LTS |

### 소프트웨어 요구 사항

- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+

---

## 개발 환경 설정

### 1. 프로젝트 클론

```bash
git clone https://github.com/your-repo/jppc.git
cd jppc
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

### 3. 개발 서버 실행

```bash
# Docker Compose로 전체 스택 실행
docker compose up -d

# 로그 확인
docker compose logs -f

# 개별 서비스 로그
docker compose logs -f backend
docker compose logs -f frontend
```

### 4. 서비스 접속

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

### 5. 개발 서버 종료

```bash
docker compose down

# 볼륨 포함 삭제 (데이터 초기화)
docker compose down -v
```

---

## 프로덕션 배포

### 1. 서버 준비

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 설치
sudo apt-get update
sudo apt-get install docker-compose-plugin

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
```

### 2. 프로젝트 배포

```bash
# 프로젝트 클론
git clone https://github.com/your-repo/jppc.git
cd jppc

# 환경 변수 설정
cp .env.example .env.prod
nano .env.prod  # 프로덕션 값 설정
```

### 3. 프로덕션 실행

```bash
# 프로덕션 이미지 빌드 및 실행
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# 상태 확인
docker compose -f docker-compose.prod.yml ps
```

### 4. SSL 인증서 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt-get install certbot

# 인증서 발급 (nginx 중지 후)
docker compose -f docker-compose.prod.yml stop nginx
sudo certbot certonly --standalone -d your-domain.com

# 인증서 복사
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/

# nginx.conf에서 HTTPS 설정 활성화 후 재시작
docker compose -f docker-compose.prod.yml up -d nginx
```

### 5. 자동 갱신 설정

```bash
# crontab에 추가
0 0 1 * * certbot renew --quiet && docker compose -f /path/to/jppc/docker-compose.prod.yml restart nginx
```

---

## 환경 변수

### 필수 환경 변수

```bash
# 데이터베이스
DB_USER=jppc
DB_PASSWORD=your_secure_password
DB_NAME=jppc

# 보안
SECRET_KEY=your_very_secure_secret_key_32_chars

# CORS
CORS_ORIGINS=https://your-domain.com
```

### 선택 환경 변수

```bash
# 이메일 (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=noreply@your-domain.com

# API
API_URL=https://your-domain.com

# 로깅
LOG_LEVEL=INFO

# 포트
HTTP_PORT=80
HTTPS_PORT=443
```

### 환경별 설정 파일

| 파일 | 용도 |
|------|------|
| `.env` | 로컬 개발 환경 |
| `.env.prod` | 프로덕션 환경 |
| `.env.test` | 테스트 환경 |

---

## 데이터베이스 마이그레이션

### 초기 마이그레이션

```bash
# 컨테이너 내부에서 실행
docker compose exec backend alembic upgrade head
```

### 새 마이그레이션 생성

```bash
docker compose exec backend alembic revision --autogenerate -m "Add new table"
```

### 마이그레이션 롤백

```bash
# 한 단계 롤백
docker compose exec backend alembic downgrade -1

# 특정 버전으로 롤백
docker compose exec backend alembic downgrade abc123
```

### 마이그레이션 상태 확인

```bash
docker compose exec backend alembic current
docker compose exec backend alembic history
```

---

## 모니터링

### 헬스 체크

```bash
# API 헬스 체크
curl http://localhost:8000/health

# 응답 예시
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### 로그 모니터링

```bash
# 전체 로그
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f backend --tail 100

# 에러만 필터링
docker compose logs backend 2>&1 | grep -i error
```

### 리소스 모니터링

```bash
# 컨테이너 상태
docker compose ps

# 리소스 사용량
docker stats
```

### 크롤링 상태 확인

```bash
# API를 통해 확인
curl http://localhost:8000/api/v1/crawling/status

# 로그 조회
curl http://localhost:8000/api/v1/crawling/logs
```

---

## 백업 및 복원

### 데이터베이스 백업

```bash
# 백업 스크립트
docker compose exec db pg_dump -U jppc jppc > backup/db_$(date +%Y%m%d_%H%M%S).sql

# 압축 백업
docker compose exec db pg_dump -U jppc jppc | gzip > backup/db_$(date +%Y%m%d_%H%M%S).sql.gz
```

### 자동 백업 설정

```bash
# /etc/cron.d/jppc-backup
0 2 * * * root cd /path/to/jppc && docker compose exec -T db pg_dump -U jppc jppc | gzip > backup/db_$(date +\%Y\%m\%d).sql.gz
```

### 데이터베이스 복원

```bash
# 복원
cat backup/db_20260131.sql | docker compose exec -T db psql -U jppc jppc

# 압축 파일 복원
gunzip -c backup/db_20260131.sql.gz | docker compose exec -T db psql -U jppc jppc
```

### 백업 파일 정리

```bash
# 30일 이상 된 백업 삭제
find backup/ -name "db_*.sql*" -mtime +30 -delete
```

---

## 트러블슈팅

### 일반적인 문제

#### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker compose logs backend

# 컨테이너 상태 확인
docker compose ps -a

# 재시작
docker compose restart backend
```

#### 데이터베이스 연결 실패

```bash
# DB 컨테이너 상태 확인
docker compose exec db pg_isready -U jppc

# 환경 변수 확인
docker compose exec backend env | grep DATABASE
```

#### 크롤링 실패

```bash
# Playwright 브라우저 확인
docker compose exec backend playwright install chromium

# 메모리 확인
docker stats jppc-backend
```

#### 디스크 공간 부족

```bash
# Docker 정리
docker system prune -a -f

# 미사용 볼륨 정리
docker volume prune -f
```

### 성능 문제

#### 느린 API 응답

```bash
# 데이터베이스 연결 풀 확인
docker compose exec db psql -U jppc -c "SELECT count(*) FROM pg_stat_activity;"

# 인덱스 확인
docker compose exec db psql -U jppc -c "\di"
```

#### 높은 메모리 사용

```bash
# 컨테이너 메모리 제한 확인
docker compose -f docker-compose.prod.yml config | grep memory

# 워커 수 조정
# backend Dockerfile의 --workers 값 조정
```

### 로그 분석

```bash
# 에러 로그 추출
docker compose logs backend 2>&1 | grep -E "(ERROR|CRITICAL)" > errors.log

# 크롤링 실패 로그
docker compose logs backend 2>&1 | grep -i "crawl.*fail"
```

---

## 업데이트 절차

### 1. 백업

```bash
docker compose exec db pg_dump -U jppc jppc > backup/pre_update_$(date +%Y%m%d).sql
```

### 2. 코드 업데이트

```bash
git pull origin main
```

### 3. 이미지 재빌드

```bash
docker compose -f docker-compose.prod.yml build --no-cache
```

### 4. 마이그레이션

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 5. 재시작

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 6. 검증

```bash
curl http://localhost:8000/health
```

---

_문서 버전: 1.0_
_최종 수정: 2026-01-31_
