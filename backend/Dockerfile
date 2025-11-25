# Python 3.14 기반 이미지 사용
FROM python:3.14-slim

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# Django 정적 파일 수집을 위한 디렉터리 생성
RUN mkdir -p /app/staticfiles /app/media

# 🚩 빌드할 때 static 모으기
RUN python manage.py collectstatic --noinput

# 포트 8000 노출
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Django 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]