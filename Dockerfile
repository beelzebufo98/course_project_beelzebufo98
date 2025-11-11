# syntax=docker/dockerfile:1.7-labs
FROM python:3.11.8-slim AS build
WORKDIR /app
COPY pyproject.toml poetry.lock* requirements*.txt* ./
RUN --mount=type=cache,target=/root/.cache \
    python -m pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.11.8-slim AS runtime

LABEL org.opencontainers.image.title="SecDev Course App" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.authors="beelzebufo98"

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY --from=build /wheels /wheels
RUN --mount=type=cache,target=/root/.cache \
    pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY . .

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import http.client; \
conn=http.client.HTTPConnection('127.0.0.1',8000,timeout=2); \
conn.request('GET','/health'); \
exit(0) if conn.getresponse().status==200 else exit(1)"

EXPOSE 8000
USER app
ENTRYPOINT ["uvicorn"]
CMD ["app.main:app","--host","0.0.0.0","--port","8000"]
