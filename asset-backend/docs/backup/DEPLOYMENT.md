# 배포 가이드

KStock Reporter 프로젝트 배포 가이드입니다.

## 목차

1. [배포 전 체크리스트](#배포-전-체크리스트)
2. [Docker Compose 배포](#docker-compose-배포)
3. [클라우드 배포](#클라우드-배포)
4. [환경 변수 설정](#환경-변수-설정)
5. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
6. [모니터링 설정](#모니터링-설정)
7. [트러블슈팅](#트러블슈팅)

## 배포 전 체크리스트

### 필수 설정

- [ ] `DJANGO_SECRET_KEY` 변경
- [ ] `DJANGO_DEBUG=false` 설정
- [ ] `ALLOWED_HOSTS` 설정
- [ ] 데이터베이스 백업
- [ ] SSL/TLS 인증서 설정
- [ ] 방화벽 규칙 설정
- [ ] Sentry DSN 설정
- [ ] 이메일 설정 (운영 환경)

### 보안 체크

- [ ] 비밀번호 정책 확인
- [ ] CORS 설정 검토
- [ ] Rate Limiting 설정
- [ ] SQL Injection 방어 확인
- [ ] XSS 방어 확인

## Docker Compose 배포

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# 운영 환경 설정
nano .env
```

`.env` 파일 필수 수정 사항:

```bash
DJANGO_ENV=production
DJANGO_SECRET_KEY=your-secure-secret-key-here
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 데이터베이스
POSTGRES_PASSWORD=secure-password-here

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-here

# Sentry
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 2. 컨테이너 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f web
docker-compose logs -f api
```

### 3. 초기 설정

```bash
# 마이그레이션
docker-compose exec web python manage.py migrate

# 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput

# 슈퍼유저 생성
docker-compose exec web python manage.py createsuperuser

# 주식 데이터 초기 동기화 (선택)
docker-compose exec web python manage.py sync_korea_stocks
```

### 4. 서비스 확인

```bash
# Django Admin
http://yourdomain.com/admin/

# FastAPI Docs
http://yourdomain.com:8001/api/docs

# Flower (Celery 모니터링)
http://yourdomain.com:5555
```

## 클라우드 배포

### AWS EC2 배포

#### 1. EC2 인스턴스 생성

```bash
# 인스턴스 타입: t3.medium 이상 권장
# OS: Ubuntu 22.04 LTS
# 보안 그룹:
#   - HTTP (80)
#   - HTTPS (443)
#   - SSH (22)
#   - Custom TCP (8000, 8001, 5555)
```

#### 2. 서버 설정

```bash
# 서버 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. 프로젝트 배포

```bash
# Git 저장소 클론
git clone https://github.com/your-org/kstock-reporter.git
cd kstock-reporter

# 환경 변수 설정
nano .env

# 배포
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### 4. Nginx 리버스 프록시 (선택)

```bash
# Nginx 설치
sudo apt install nginx -y

# 설정 파일 생성
sudo nano /etc/nginx/sites-available/kstock-reporter
```

Nginx 설정:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/kstock-reporter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. SSL 인증서 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx -y

# SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

### Heroku 배포

#### 1. Heroku CLI 설치

```bash
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

#### 2. 앱 생성 및 배포

```bash
# Heroku 앱 생성
heroku create your-app-name

# PostgreSQL 추가
heroku addons:create heroku-postgresql:mini

# Redis 추가
heroku addons:create heroku-redis:mini

# 환경 변수 설정
heroku config:set DJANGO_ENV=production
heroku config:set DJANGO_SECRET_KEY=your-secret-key
heroku config:set DJANGO_DEBUG=false

# 배포
git push heroku main

# 마이그레이션
heroku run python manage.py migrate

# 슈퍼유저 생성
heroku run python manage.py createsuperuser
```

## 환경 변수 설정

### 필수 환경 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `DJANGO_ENV` | 환경 설정 | production |
| `DJANGO_SECRET_KEY` | Django 시크릿 키 | random-50-char-string |
| `DJANGO_DEBUG` | 디버그 모드 | false |
| `DJANGO_ALLOWED_HOSTS` | 허용 호스트 | yourdomain.com |
| `POSTGRES_DB` | DB 이름 | kstock |
| `POSTGRES_USER` | DB 사용자 | kstock_user |
| `POSTGRES_PASSWORD` | DB 비밀번호 | secure-password |
| `JWT_SECRET_KEY` | JWT 시크릿 | random-string |
| `SENTRY_DSN` | Sentry DSN | https://... |

### 선택 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `REDIS_URL` | Redis URL | redis://redis:6379/2 |
| `CELERY_BROKER_URL` | Celery 브로커 | redis://redis:6379/0 |
| `KAKAO_API_HOST` | 카카오 API | - |
| `EMAIL_HOST` | 이메일 호스트 | smtp.gmail.com |

## 데이터베이스 마이그레이션

### 마이그레이션 실행

```bash
# 개발 환경
python manage.py migrate

# Docker 환경
docker-compose exec web python manage.py migrate

# 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 롤백
python manage.py migrate app_name migration_name
```

### 데이터베이스 백업

```bash
# PostgreSQL 백업
docker-compose exec db pg_dump -U kstock_user kstock > backup.sql

# 복원
docker-compose exec -T db psql -U kstock_user kstock < backup.sql

# 자동 백업 스크립트
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U kstock_user kstock | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
find $BACKUP_DIR -mtime +7 -delete  # 7일 이상 된 백업 삭제
```

## 모니터링 설정

### Sentry 설정

1. Sentry.io 계정 생성
2. 프로젝트 생성
3. DSN 복사
4. `.env` 파일에 추가:

```bash
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
RELEASE_VERSION=1.0.0
```

### Flower (Celery 모니터링)

```bash
# 접속
http://yourdomain.com:5555

# 기본 인증 추가 (권장)
FLOWER_BASIC_AUTH=user:password
```

### 로그 모니터링

```bash
# 실시간 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f web api celery-worker

# 로그 파일 위치
logs/django.log
logs/error.log
logs/celery.log
logs/stocks.log
```

## 트러블슈팅

### 일반적인 문제

#### 1. 데이터베이스 연결 실패

```bash
# 데이터베이스 상태 확인
docker-compose ps
docker-compose logs db

# 재시작
docker-compose restart db web
```

#### 2. Celery 작업 실행 안 됨

```bash
# Celery 상태 확인
docker-compose logs celery-worker
docker-compose logs celery-beat

# Redis 연결 확인
docker-compose exec redis redis-cli ping

# Celery 재시작
docker-compose restart celery-worker celery-beat
```

#### 3. 정적 파일 404

```bash
# 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput

# 권한 확인
docker-compose exec web ls -la staticfiles/
```

#### 4. API 응답 느림

```bash
# 데이터베이스 쿼리 최적화
# - select_related() 사용
# - prefetch_related() 사용
# - 인덱스 추가

# Redis 캐시 확인
docker-compose exec redis redis-cli
> INFO keyspace
> KEYS kstock:*

# 로그 확인
docker-compose logs -f api
```

### 성능 최적화

#### 1. Gunicorn 워커 수 조정

```yaml
# docker-compose.yml
command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2
```

#### 2. Uvicorn 워커 수 조정

```yaml
# docker-compose.yml
command: uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

#### 3. 데이터베이스 커넥션 풀

```python
# settings/production.py
DATABASES['default']['CONN_MAX_AGE'] = 600
```

## 보안 체크리스트

- [ ] SECRET_KEY 변경
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS 설정
- [ ] HTTPS 강제
- [ ] HSTS 설정
- [ ] CSRF 보호 활성화
- [ ] SQL Injection 방어
- [ ] XSS 방어
- [ ] Rate Limiting 활성화
- [ ] 비밀번호 정책 강화
- [ ] 정기적인 보안 업데이트
- [ ] 로그 모니터링
- [ ] 백업 자동화

## 추가 리소스

- [Django 배포 체크리스트](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Docker 보안 가이드](https://docs.docker.com/engine/security/)
- [Celery 배포 가이드](https://docs.celeryq.dev/en/stable/userguide/daemonizing.html)
