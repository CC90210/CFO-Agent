# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Builder
# Installs all Python dependencies into a virtual environment so only the
# compiled site-packages are copied into the final image, keeping it lean.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Prevents Python from writing .pyc files and buffering stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# System packages required to compile some Python extensions (ta-lib, numpy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        libffi-dev \
        libssl-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to isolate dependencies.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip inside the venv first.
RUN pip install --upgrade pip

# Install project dependencies (no dev extras — no pytest in the image).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Runtime
# Minimal image: copy venv + source, run as non-root.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# UTC timezone — all timestamps logged and stored in UTC.
# Force UTF-8 so box-drawing characters render correctly in log files.
ENV TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        curl \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Copy the pre-built virtual environment from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Create a non-root user so the agent does not run as root.
RUN groupadd --gid 1001 atlas && \
    useradd --uid 1001 --gid atlas --shell /bin/bash --create-home atlas

WORKDIR /app

# Copy source code (honoring .dockerignore).
COPY --chown=atlas:atlas . .

# Create the logs directory and ensure the db path is writable.
# The compose file mounts these as named volumes, but the directory must
# exist in the image so Python's FileHandler does not fail on first start.
RUN mkdir -p /app/logs /app/data && \
    chown -R atlas:atlas /app

USER atlas

# Verify the application can import its own configuration at build time.
# Uses safe defaults (PAPER_TRADE=true) so no .env file is required during build.
# This catches broken requirements or missing modules before deployment.
RUN PAPER_TRADE=true python -c "from config.settings import settings; print('Config OK')"

# Atlas is a headless agent — no ports are exposed.
# The paper_trade.py dashboard writes to the log file and stdout only.

# Health check: confirm the Python process and core module are importable.
# Runs every 60 s, gives a 30 s grace period at startup, 3 retries before
# the container is marked unhealthy.
HEALTHCHECK --interval=60s --timeout=15s --start-period=30s --retries=3 \
    CMD python -c "from config.settings import settings; from core.engine import TradingEngine" || exit 1

# Default: run the standalone paper trading dashboard.
# Override with: docker run atlas-trader python main.py backtest --strategy all ...
CMD ["python", "paper_trade.py"]
