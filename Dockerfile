FROM ubuntu

RUN apt update
RUN apt install -y netcat-openbsd

WORKDIR /app

RUN apt install -y python3-venv
RUN python3 -m venv .venv
RUN . .venv/bin/activate

RUN apt install -y python3-pip

RUN python3 -m pip install --break-system-packages uvicorn
RUN python3 -m pip install --break-system-packages "fastapi[all]"
RUN python3 -m pip install --break-system-packages sqlalchemy psycopg2-binary pydantic python-jose passlib python-multipart
