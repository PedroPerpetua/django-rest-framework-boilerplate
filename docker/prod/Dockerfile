ARG PYTHON=python:3.14.5-bookworm

# Building stage +++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON} AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
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
RUN uv sync --frozen --active \
    --no-default-groups \
    --group boilerplate \
    --group boilerplate-prod

# Final stage ++++++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON}

# Setting up python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Add runtime dependencies -------------------------------
RUN apt-get update

# Setup Supervisor + nginx -------------------------------
RUN apt-get install -y nginx=1.22.1-9+deb12u7
COPY ./docker/prod/nginx.conf.template /etc/nginx/nginx.conf.template
COPY ./docker/prod/supervisord.ini /etc/supervisor.d/supervisord.ini
RUN chown -R www-data:www-data /var/lib/nginx

# Copy Python environment --------------------------------
COPY --from=builder /venv /venv
ENV PATH=/venv/bin:$PATH

# Copy the app -------------------------------------------
COPY ./app /app
WORKDIR /app

# Set up the entrypoint and run
COPY ./docker/prod/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
