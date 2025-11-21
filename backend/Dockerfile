# Python 3.14 기반 이미지 사용
FROM python:3.14-slim

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL 클라이언트 포함)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# wait-for-it.sh 스크립트 복사 및 실행 권한 부여
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# 소스 코드 복사
COPY . .

# Django 정적 파일 수집을 위한 디렉터리 생성
RUN mkdir -p /app/staticfiles

# 포트 8000 노출
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# wait-for-it.sh를 사용하여 데이터베이스 준비 대기 후 Django 서버 실행
CMD ["wait-for-it.sh", "db:5432", "--", "python", "manage.py", "runserver", "0.0.0.0:8000"]