import mysql.connector

def test_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Gopal@143"  # Use your actual MySQL password
        )
        print("✅ Successfully connected to MySQL!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()