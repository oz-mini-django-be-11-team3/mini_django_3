# 베이스 이미지
FROM python:3.13-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

# 필수 패키지 설치 (uv 실행 및 빌드 도구 등)
RUN apt-get update && apt-get install -y curl build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock

# 작업 디렉토리 설정
WORKDIR /app

# pyproject.toml & uv.lock 설치
RUN uv sync --all-packages && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

# 애플리케이션 코드 복사
COPY ./app ./app

# 포트 설정 (FastAPI일 경우도 동일)
EXPOSE 8000

# Gunicorn + UvicornWorker 실행
#CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]

# 스크립트를 사용하여 애플리케이션 실행
#COPY app/scripts .
#RUN chmod +x /scripts/run.sh
#CMD ["/scripts/run.sh"]
