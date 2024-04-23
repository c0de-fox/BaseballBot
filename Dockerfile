# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

# Build with: docker build -t baseballbot:<version> .
# Run with: docker run -it

FROM python:3.10-alpine3.16 AS build

RUN pip install --no-cache-dir discord peewee
WORKDIR /app
COPY . .

FROM build AS run

ENV discord_token ""
ENV database_path "/tmp/baseball.db"

CMD ["python", "-u", "/app/main.py"]