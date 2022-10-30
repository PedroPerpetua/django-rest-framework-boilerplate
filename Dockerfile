FROM python:3.11-alpine
LABEL maintainer PedroPerpetua

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Add dependencies ---------------------------------------
RUN apk update

# Python requirements ------------------------------------
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy the app and config --------------------------------
COPY ./app /app
COPY ./config.yaml /app/config.yaml

WORKDIR /app
