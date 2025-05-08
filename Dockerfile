FROM python:3.12

RUN apt update
RUN apt-get -y install build-essential libssl-dev libffi-dev libblas3 libc6 liblapack3 gcc python3-dev python3-pip cython3
RUN apt install netcat-traditional
RUN apt install -y libpq-dev python3-dev

WORKDIR /app

RUN apt install -y ubuntu-mate-desktop^ net-tools python3-pip python3-tk uvicorn
RUN pip install fastapi sqlalchemy psycopg2 pydantic python-jose passlib[bcrypt]

CMD ["python", "-m", "app.main"]
