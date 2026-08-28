ARG PYTHON=python:3.14.7-slim-bookworm

# Building stage +++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON} AS builder

ENV UV_LINK_MODE=copy
ENV UV_FROZEN=1
ENV UV_NO_EDITABLE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_PYTHON_DOWNLOADS=0

# Add build-time dependencies ----------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # For psycopg2
    build-essential=12.9 \
    libpq-dev=15.19-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/*

# Install and configure uv -------------------------------
COPY --from=ghcr.io/astral-sh/uv:0.12.4 /uv /uvx /bin/
RUN uv venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:${PATH}"

# Install Python requirements ----------------------------
WORKDIR /project
COPY ./pyproject.toml ./uv.lock ./
COPY ./app/pyproject.toml ./app/pyproject.toml
RUN uv sync --active

# Final stage ++++++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON}

# Disable ruff cache
ENV RUFF_NO_CACHE=true

# Add runtime dependencies -------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # For psycopg2
    libpq5=15.19-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment --------------------------------
COPY --from=builder /venv /venv
ENV PATH=/venv/bin:$PATH

# Copy the app ------------------------------------------
COPY ./app /app
WORKDIR /app
# Copy additional files required for linting
COPY ./typing /typing

# Set up the entrypoint and run
COPY ./docker/dev/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
