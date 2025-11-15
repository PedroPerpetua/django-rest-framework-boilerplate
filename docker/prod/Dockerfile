ARG PYTHON=python:3.14.0-alpine

# Building stage +++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON} AS builder

# Add build-time dependencies ----------------------------
RUN apk update
# For psycopg2
RUN apk add --no-cache build-base libpq libpq-dev

# Create venv --------------------------------------------
RUN python3 -m venv --upgrade-deps /venv
ENV PATH=/venv/bin:$PATH

# Install Python requirements ----------------------------
COPY ./requirements /requirements
RUN pip install --no-compile --no-cache-dir -r /requirements/requirements.txt
# For production
RUN pip install --no-compile --no-cache-dir gunicorn supervisor

# Final stage ++++++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON}

# Setting up python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add runtime dependencies -------------------------------
RUN apk update
# For psycopg2
RUN apk add --no-cache libpq

# Setup Supervisor + nginx -------------------------------
RUN apk --no-cache add nginx
COPY ./docker/prod/nginx.conf.template /etc/nginx/nginx.conf.template
COPY ./docker/prod/supervisord.ini /etc/supervisor.d/supervisord.ini
RUN chown -R nginx:nginx /var/lib/nginx

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
