# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# Multistage docker file, using a very minimal 17.6 MB base image
# Results in a cross-platform 76 MB image including all dependencies
# Build with: docker build -t ghotballbot:<version> .
# Run with: docker run -it

FROM python:3.10-alpine3.16 AS build

RUN pip install discord peewee
COPY . /app

FROM build AS run

ENV discord_token ""
ENV database_path "/tmp/ghostball.db"

WORKDIR /app
CMD ["python", "/app/main.py"]
