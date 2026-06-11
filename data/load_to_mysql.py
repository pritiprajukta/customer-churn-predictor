import pandas as pd
import mysql.connector

df = pd.read_csv('data/churn_raw.csv')

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Priti@1234',
    database='churn_db'
)

cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO customers VALUES 
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, tuple(row))

conn.commit()
cursor.close()
conn.close()
print("✅ Data loaded into MySQL successfully!")