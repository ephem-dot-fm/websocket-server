import psycopg2
from sqlalchemy import create_engine

import os
from dotenv import load_dotenv
load_dotenv()

def connect_to_pg_normal():
    connection = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = connection.cursor()
    return [connection, cursor]

def connect_to_pg_dataframe():
    db = create_engine(os.getenv('DATABASE_URL'))
    conn = db.connect()
    return conn