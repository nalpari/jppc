# ============================================
# Stage 1: Base image with system dependencies
# ============================================
FROM python:3.12-slim AS base

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ============================================
# Stage 2: Python dependencies builder
# ============================================
FROM base AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
RUN playwright install chromium && \
    playwright install-deps chromium

# ============================================
# Stage 3: Development image
# ============================================
FROM python:3.12-slim AS development

WORKDIR /app

# Install Playwright browser dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Playwright deps in this stage
RUN playwright install-deps chromium

# Copy Playwright browsers
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY . .

EXPOSE 8000

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Stage 4: Production image
# ============================================
FROM python:3.12-slim AS production

WORKDIR /app

# Install minimal dependencies and create user
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Playwright deps
RUN playwright install-deps chromium

# Copy Playwright browsers
COPY --from=builder /root/.cache/ms-playwright /home/appuser/.cache/ms-playwright
RUN chown -R appuser:appuser /home/appuser/.cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8000

# Production command with multiple workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
