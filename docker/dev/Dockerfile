ARG PYTHON=python:3.13.5-alpine

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


CMD sh -c "python manage.py setup \
           && python manage.py runserver 0.0.0.0"
