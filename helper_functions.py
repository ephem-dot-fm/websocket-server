import psycopg2
from sqlalchemy import create_engine

import os
from dotenv import load_dotenv
load_dotenv()

def connect_to_pg_normal():
    connection = psycopg2.connect(os.getenv('POSTGRES_CONNECTION_URI'))
    cursor = connection.cursor()
    return [connection, cursor]

def connect_to_pg_dataframe():
    db = create_engine(os.getenv('POSTGRES_CONNECTION_URI'))
    conn = db.connect()
    return conn