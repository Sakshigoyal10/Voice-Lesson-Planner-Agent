"""
Database setup and initialization script
Run this before starting the application for the first time
"""

import os
import sys
from database import init_db, drop_all_tables, engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()


def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. DATABASE_URL in .env is correct")
        print("3. Database exists and user has permissions")
        return False


def setup_database(reset=False):
    """Set up database tables"""
    print("=" * 60)
    print("🗄️ KVS Lesson Plan Database Setup")
    print("=" * 60)

    if not check_database_connection():
        sys.exit(1)

    if reset:
        confirm = input("\n⚠️ WARNING: This will delete ALL data! Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            print("\n🗑️ Dropping all tables...")
            drop_all_tables()
        else:
            print("❌ Reset cancelled.")
            return

    print("\n📦 Creating database tables...")
    init_db()

    print("\n✅ Database setup complete!")
    print("\nTables created:")
    print(" - transcripts (stores voice transcripts)")
    print(" - lesson_plans (stores lesson plan metadata)")
    print(" - lesson_sessions (stores individual sessions)")
    print("\n🚀 You can now start the application with:")
    print(" python main.py")
    print("=" * 60)


def show_database_info():
    """Show current database information"""
    from database import SessionLocal
    import crud

    db = SessionLocal()
    try:
        stats = crud.get_statistics(db)

        print("\n" + "=" * 60)
        print("📊 Database Statistics")
        print("=" * 60)

        print(f"Total Transcripts: {stats['total_transcripts']}")
        print(f"Total Lesson Plans: {stats['total_lessons']}")
        print(f"Total Sessions: {stats['total_sessions']}")

        if stats['subjects_distribution']:
            print("\n📚 Subjects Distribution:")
            for subject, count in stats['subjects_distribution'].items():
                print(f" - {subject}: {count}")

        print("=" * 60 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KVS Lesson Plan Database Setup")
    parser.add_argument('--reset', action='store_true', help='Reset database (delete all data)')
    parser.add_argument('--info', action='store_true', help='Show database information')
    args = parser.parse_args()

    if args.info:
        show_database_info()
    else:
        setup_database(reset=args.reset)
