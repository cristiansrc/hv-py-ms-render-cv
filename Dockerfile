FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create non-root user (rendercv, UID 1000, GID 1000)
RUN groupadd -g 1000 rendercv && \
    useradd -u 1000 -g rendercv -m rendercv

# Install production dependencies only (lines before "# Dev dependencies")
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir \
    $(awk 'BEGIN{found=0} /^# Dev dependencies/{found=1} found==0{print}' /app/requirements.txt \
    | grep -v '^#' | grep -v '^$' | tr '\n' ' ')

# Copy application code and set ownership
COPY . /app
RUN chown -R rendercv:rendercv /app

# Switch to non-root user
USER rendercv

# Health check: GET /health endpoint
# Uses python directly since python:3.12-slim does not include curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "30"]
