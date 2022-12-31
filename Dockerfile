ARG PYTHON=python:3.11-alpine

# Building stage +++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON} AS builder

# Add build-time dependencies ----------------------------
RUN apk update

# Create venv --------------------------------------------
RUN python3 -m venv /venv
ENV PATH=/venv/bin:$PATH

# Install Python requirements ----------------------------
COPY ./requirements /requirements
RUN pip install -r /requirements/requirements.txt

# Final stage ++++++++++++++++++++++++++++++++++++++++++++
FROM ${PYTHON}

# Add runtime dependencies -------------------------------
RUN apk update

# Copy Python environment --------------------------------
COPY --from=builder /venv/ /venv
ENV PATH=/venv/bin:$PATH

# Copy the app ------------------------------------------
COPY ./app /app
WORKDIR /app

CMD sh -c "python manage.py setup \
           && python manage.py runserver 0.0.0.0"
