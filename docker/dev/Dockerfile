ARG PYTHON=python:3.14.5-bookworm

# Building stage +++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON} AS builder

ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

# Add build-time dependencies ----------------------------
RUN apt-get update

# Install and configure uv -------------------------------
COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /uvx /bin/
RUN uv venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:${PATH}"

# Install Python requirements ----------------------------
WORKDIR /project
COPY ./pyproject.toml ./uv.lock ./
COPY ./app/pyproject.toml ./app/pyproject.toml
RUN uv sync --frozen --active

# Final stage ++++++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON}

# Disable ruff cache
ENV RUFF_NO_CACHE=true

# Add runtime dependencies -------------------------------
RUN apt-get update

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
