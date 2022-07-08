FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /code
COPY pyproject.toml /code/
COPY poetry.lock /code/
COPY web-entrypoint.sh /usr/local/bin

RUN apt-get update
RUN apt-get -y install python3-pip
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install
RUN apt update
RUN apt -y install celery
RUN chmod +x /usr/local/bin/web-entrypoint.sh



COPY . /code/
ENTRYPOINT /usr/local/bin/web-entrypoint.sh



