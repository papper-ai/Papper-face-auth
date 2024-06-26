FROM python:3.11-slim
LABEL authors="pomelk1n"

WORKDIR /usr/data/app

COPY requirements/base.txt requirements/

RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

RUN apt-get update && apt-get install iputils-ping ffmpeg libsm6 libxext6 -y
RUN pip install --no-cache-dir -r requirements/base.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -r requirements

COPY . .

ENV PYTHONPATH=/usr/data/app/

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "src/uvicorn-logging-config.yaml"]