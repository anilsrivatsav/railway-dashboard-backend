import os
from database import Base, engine

DB_FILE = "stations_units_earnings.db"

if os.path.exists(DB_FILE):
    print(f"🔨 Deleting existing database: {DB_FILE}")
    os.remove(DB_FILE)
else:
    print(f"✅ No existing database found, creating fresh.")

print("🚀 Creating new tables from models...")
Base.metadata.create_all(bind=engine)

print("✅ Database reset complete! 🎉")