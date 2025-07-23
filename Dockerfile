FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

RUN apt-get update && apt-get install -y curl build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock

WORKDIR /app

RUN uv sync --all-packages && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

COPY ./app ./

# ⬇️ run.sh를 scripts 디렉토리에 넣고 절대 경로 사용
COPY run.sh /scripts/run.sh
RUN chmod +x /scripts/run.sh

EXPOSE 8000

# ✅ 절대 경로로 정확히 명시
CMD ["/scripts/run.sh"]