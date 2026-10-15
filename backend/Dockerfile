# ==============================================================================
# Backend Dockerfile for AI Company Brochure Generator
# Python 3.12 slim, multi-user least privilege, non-root execution
# ==============================================================================

FROM python:3.12-slim-bookworm

# Set runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Create a non-root system user and group for security
RUN groupadd --system --gid 1001 appgroup && \
    useradd --system --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

WORKDIR /app

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code into /app/backend
COPY . ./backend/

# Adjust file permissions for non-root execution
RUN chown -R appuser:appgroup /app

# Switch to unprivileged user
USER appuser

# Expose internal backend port (accessible only inside Docker network)
EXPOSE 8000

# Container healthcheck using standard library urllib (no curl dependency required)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')" || exit 1

# Start FastAPI application via Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
