FROM python:3.13.2-slim

RUN apt-get update && apt-get install -yq make \
                && pip install uv

WORKDIR /app

COPY . .

RUN uv sync
# RUN cp env.example .env 

CMD ["sh", "-c", "make migrate && make collectstatic && make prod-run"]