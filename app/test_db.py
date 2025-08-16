import mysql.connector
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings

# Rest of your test code...

from app.config import settings

def test_db_connection():
    try:
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        print("✅ Successfully connected to MySQL server!")
        
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        print("📦 Available databases:", [db[0] for db in cursor])
        
        if settings.DB_NAME not in [db[0] for db in cursor]:
            print(f"⚠️ Database '{settings.DB_NAME}' doesn't exist")
        else:
            print(f"✅ Database '{settings.DB_NAME}' exists")
            
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_db_connection()