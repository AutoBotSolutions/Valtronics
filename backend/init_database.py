#!/usr/bin/env python3
"""
Database initialization script for Valtronics
Creates all necessary tables in the SQLite database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session_sqlite import engine, Base
from app.models.device import Device, TelemetryData, DeviceCommand
from app.models.alert import Alert, AlertRule, AlertNotification

def init_database():
    """Initialize the database with all tables"""
    print("Initializing Valtronics database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Created tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
