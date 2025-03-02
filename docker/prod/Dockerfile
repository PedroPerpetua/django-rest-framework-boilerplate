ARG PYTHON=python:3.13.2-alpine

# Building stage +++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON} AS builder

# Add build-time dependencies ----------------------------
RUN apk update

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

# Setup Supervisor + nginx -------------------------------
RUN apk --no-cache add nginx
COPY ./docker/prod/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/prod/supervisord.ini /etc/supervisor.d/supervisord.ini
RUN chown -R nginx:nginx /var/lib/nginx

# Copy Python environment --------------------------------
COPY --from=builder /venv /venv
ENV PATH=/venv/bin:$PATH

# Copy the app -------------------------------------------
COPY ./app /app
WORKDIR /app

CMD sh -c "python manage.py setup \
           && supervisord -c /etc/supervisor.d/supervisord.ini"
