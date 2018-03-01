FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN pip install pipenv

COPY ./compose/web/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x -R /usr/local/bin

COPY . /app
RUN cd /app && pipenv install --system

WORKDIR /app

ENTRYPOINT ["docker-entrypoint.sh"]