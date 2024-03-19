FROM python:3.9 as builder
RUN pip install poetry
RUN curl -o ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy
COPY pyproject.toml poetry.lock ./
RUN /opt/conda/bin/conda create -n myenv python=3.9 && \
    /opt/conda/envs/myenv/bin/poetry install --no-dev --no-interaction --no-ansi
RUN /opt/conda/bin/conda install -c conda-forge conda-pack
RUN /opt/conda/bin/conda-pack -n myenv -o /tmp/env.tar && \
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar
FROM debian:buster as final
COPY --from=builder /venv /venv
RUN apt-get update && apt-get install -y curl && \
    curl -o ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    /opt/conda/bin/conda install -c conda-forge conda-pack && \
    /opt/conda/bin/conda-unpack
WORKDIR /app
COPY . .
CMD ["/opt/conda/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
