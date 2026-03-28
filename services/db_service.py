import pyodbc
import pandas as pd
from config import SQL_SERVER_CONN

def get_connection():
    try:
        return pyodbc.connect(SQL_SERVER_CONN)
    except pyodbc.Error as e:
        print(f"DB Error: {e}")
        return None


def fetch_table_data():
    conn = get_connection()

    if conn:
        try:
            query = "SELECT * FROM sales_data"
            df = pd.read_sql(query, conn)
            print("✅ Loaded from SQL Server")
            return df
        except Exception as e:
            print(f"SQL Error: {e}")

    try:
        df = pd.read_csv("sales_data.csv")
        print("⚠️ Using CSV backup")
        return df
    except Exception as e:
        print(f"CSV Error: {e}")
        return pd.DataFrame()