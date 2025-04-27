FROM python:3.9-slim-buster

RUN apt update
RUN apt-get -y install build-essential libssl-dev libffi-dev libblas3 libc6 liblapack3 gcc python3-dev python3-pip cython3
RUN apt install -y netcat
RUN apt install -y libpq-dev python3-dev

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install sanic sqlalchemy sanic_jinja2 psycopg2

CMD ["python", "-m", "app.main"]