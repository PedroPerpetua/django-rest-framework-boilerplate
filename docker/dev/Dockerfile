ARG PYTHON=python:3.13.7-alpine

# Building stage +++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON} AS builder

# Add build-time dependencies ----------------------------
RUN apk update
# For psycopg2
RUN apk add build-base libpq libpq-dev

# Create venv --------------------------------------------
RUN python3 -m venv --upgrade-deps /venv
ENV PATH=/venv/bin:$PATH

# Install Python requirements ----------------------------
COPY ./requirements /requirements
RUN pip install -r /requirements/dev.requirements.txt

# Final stage ++++++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON}

# Disable ruff cache
ENV RUFF_NO_CACHE=true

# Add runtime dependencies -------------------------------
RUN apk update
# For psycopg2
RUN apk add --no-cache libpq

# Copy Python environment --------------------------------
COPY --from=builder /venv/ /venv
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
