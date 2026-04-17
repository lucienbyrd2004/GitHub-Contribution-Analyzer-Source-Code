import sqlalchemy
import os
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import text
from dotenv import load_dotenv
import streamlit as st

#Setting up the connector to get into the database
ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")

#Login for the database
load_dotenv()
    
# DB_INSTANCE = os.getenv("DB_INSTANCE")
# DB_DRIVER = os.getenv("DB_DRIVER")
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")

DB_INSTANCE = st.secrets["DB_INSTANCE"]
DB_DRIVER = st.secrets["DB_DRIVER"]
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_NAME = st.secrets["DB_NAME"]


def getconn():
    conn= connector.connect(
        DB_INSTANCE,
        DB_DRIVER,
        user = DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME
    )
    return conn
pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )


def connecttodatabase():
    try:
        with pool.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("Connection Established")
    except Exception as e:
        print(f"SQLAlchemy connection failed: {e}")
        