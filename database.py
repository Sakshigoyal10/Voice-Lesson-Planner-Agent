import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite database URL (local file)
DATABASE_URL = "sqlite:///./kvs_lessonplan.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print("📁 Using SQLite database - No network/server needed!")
print(f"📍 Database file: {os.path.abspath('kvs_lessonplan.db')}")


class Transcript(Base):
    """Store voice transcripts"""
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    transcript_text = Column(Text, nullable=False)

    detected_topic = Column(String(500))
    detected_subject = Column(String(100))
    detected_class = Column(String(50))
    detected_language = Column(String(50))

    audio_duration = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    lesson_id = Column(String(50), index=True)


class LessonPlan(Base):
    """Store generated lesson plans"""
    __tablename__ = "lesson_plans"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(String(50), unique=True, index=True, nullable=False)

    topic = Column(String(500), nullable=False)
    subject = Column(String(100), nullable=False)
    class_level = Column(String(50), nullable=False)
    language = Column(String(50), nullable=False)

    num_sessions = Column(Integer, default=4)
    session_duration = Column(Integer, default=40)

    formatted_text = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LessonSession(Base):
    """Store individual sessions of lesson plans"""
    __tablename__ = "lesson_sessions"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(String(50), index=True, nullable=False)

    session_number = Column(Integer, nullable=False)
    duration = Column(String(50))

    competency = Column(Text)
    elo = Column(Text)
    activities = Column(Text)  # JSON string
    resources_tlm = Column(Text)
    worksheets = Column(String(200))
    assessment = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print(f"📍 Database file: {os.path.abspath('kvs_lessonplan.db')}")


def drop_all_tables():
    """Drop all tables - use with caution!"""
    Base.metadata.drop_all(bind=engine)
    print("🗑️ All tables dropped!")


if __name__ == "__main__":
    init_db()
    print("✅ Database helper functions ready")
