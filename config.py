import os
from dotenv import load_dotenv

print("Environment Loaded:", load_dotenv()) 


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


SQL_SERVER_CONN = (
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=SYSTEM\\SQLEXPRESS03;'
    'Database=InsightFlowDB;'
    'Trusted_Connection=yes'
)

