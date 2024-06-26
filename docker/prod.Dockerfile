FROM python:3.11-slim
LABEL authors="pomelk1n"

RUN addgroup --gid 10001 papperuser && \
    adduser --uid 10001 --gid 10001 --disabled-password --gecos "" papperuser

WORKDIR /usr/data/app

RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

COPY requirements/base.txt requirements/

RUN apt-get update && apt-get install curl ffmpeg libsm6 libxext6 -y
RUN pip install --no-cache-dir -r requirements/base.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -r requirements

COPY --chown=papperuser:papperuser . .

ENV PYTHONPATH=/usr/data/app/

USER papperuser

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "src/uvicorn-logging-config.yaml"]