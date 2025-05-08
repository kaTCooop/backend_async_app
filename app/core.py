from fastapi import FastAPI
from database import create_engine_and_tables


engine, conn, meta = create_engine_and_tables()
app = FastAPI()