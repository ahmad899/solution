FROM alpine:3.20.1 as build-image

ARG GITLAB_API_URL=https://gitlab.com/api/v4
ARG GITLAB_API_TOKEN

ENV GITLAB_API_URL=${GITLAB_API_URL} \
    GITLAB_API_TOKEN=${GITLAB_API_TOKEN}

RUN set -eux; \
    apk add --no-cache --update python3=3.12.3-r1 py3-pip

RUN adduser -D pythonuser

WORKDIR /app

COPY requirements.txt requirements.txt

RUN rm /usr/lib/python*/EXTERNALLY-MANAGED && \
    pip install --no-cache-dir -r requirements.txt

COPY gitlab-api.py gitlab-api.py

RUN chown -R pythonuser:pythonuser /app

USER pythonuser

ENTRYPOINT  [ "python3", "gitlab-api.py" ]