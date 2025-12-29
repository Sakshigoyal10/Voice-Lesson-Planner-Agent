from sqlalchemy.orm import Session
from database import Transcript, LessonPlan, LessonSession
from datetime import datetime
from typing import List, Optional
import json


# ============ Transcript Operations ============

def create_transcript(
    db: Session,
    transcript_text: str,
    detected_topic: Optional[str] = None,
    detected_subject: Optional[str] = None,
    detected_class: Optional[str] = None,
    detected_language: Optional[str] = None,
    audio_duration: Optional[float] = None,
    lesson_id: Optional[str] = None
) -> Transcript:
    """Create a new transcript record"""
    transcript = Transcript(
        transcript_text=transcript_text,
        detected_topic=detected_topic,
        detected_subject=detected_subject,
        detected_class=detected_class,
        detected_language=detected_language,
        audio_duration=audio_duration,
        lesson_id=lesson_id
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


def get_transcript_by_id(db: Session, transcript_id: int) -> Optional[Transcript]:
    """Get transcript by ID"""
    return db.query(Transcript).filter(Transcript.id == transcript_id).first()


def get_transcripts_by_lesson_id(db: Session, lesson_id: str) -> List[Transcript]:
    """Get all transcripts for a lesson"""
    return db.query(Transcript).filter(Transcript.lesson_id == lesson_id).all()


def get_recent_transcripts(db: Session, limit: int = 10) -> List[Transcript]:
    """Get recent transcripts"""
    return db.query(Transcript).order_by(Transcript.created_at.desc()).limit(limit).all()


def search_transcripts(db: Session, search_term: str, limit: int = 20) -> List[Transcript]:
    """Search transcripts by text content"""
    return db.query(Transcript).filter(
        Transcript.transcript_text.ilike(f"%{search_term}%")
    ).order_by(Transcript.created_at.desc()).limit(limit).all()


# ============ Lesson Plan Operations ============

def create_lesson_plan(
    db: Session,
    lesson_id: str,
    topic: str,
    subject: str,
    class_level: str,
    language: str,
    num_sessions: int,
    session_duration: int,
    formatted_text: str
) -> LessonPlan:
    """Create a new lesson plan"""
    lesson = LessonPlan(
        lesson_id=lesson_id,
        topic=topic,
        subject=subject,
        class_level=class_level,
        language=language,
        num_sessions=num_sessions,
        session_duration=session_duration,
        formatted_text=formatted_text
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def get_lesson_plan_by_id(db: Session, lesson_id: str) -> Optional[LessonPlan]:
    """Get lesson plan by lesson_id"""
    return db.query(LessonPlan).filter(LessonPlan.lesson_id == lesson_id).first()


def get_recent_lesson_plans(db: Session, limit: int = 10) -> List[LessonPlan]:
    """Get recent lesson plans"""
    return db.query(LessonPlan).order_by(LessonPlan.created_at.desc()).limit(limit).all()


def search_lesson_plans(
    db: Session,
    topic: Optional[str] = None,
    subject: Optional[str] = None,
    class_level: Optional[str] = None,
    limit: int = 20
) -> List[LessonPlan]:
    """Search lesson plans by filters"""
    query = db.query(LessonPlan)
    
    if topic:
        query = query.filter(LessonPlan.topic.ilike(f"%{topic}%"))
    if subject:
        query = query.filter(LessonPlan.subject == subject)
    if class_level:
        query = query.filter(LessonPlan.class_level == class_level)
    
    return query.order_by(LessonPlan.created_at.desc()).limit(limit).all()


def update_lesson_plan(db: Session, lesson_id: str, formatted_text: str) -> Optional[LessonPlan]:
    """Update lesson plan text"""
    lesson = get_lesson_plan_by_id(db, lesson_id)
    if lesson:
        lesson.formatted_text = formatted_text
        lesson.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lesson)
    return lesson


def delete_lesson_plan(db: Session, lesson_id: str) -> bool:
    """Delete lesson plan and associated sessions"""
    lesson = get_lesson_plan_by_id(db, lesson_id)
    if lesson:
        # Delete associated sessions
        db.query(LessonSession).filter(LessonSession.lesson_id == lesson_id).delete()
        # Delete lesson
        db.delete(lesson)
        db.commit()
        return True
    return False


# ============ Session Operations ============

def create_lesson_session(
    db: Session,
    lesson_id: str,
    session_number: int,
    duration: str,
    competency: str,
    elo: str,
    activities: List[str],
    resources_tlm: str,
    worksheets: str,
    assessment: str
) -> LessonSession:
    """Create a lesson session"""
    session = LessonSession(
        lesson_id=lesson_id,
        session_number=session_number,
        duration=duration,
        competency=competency,
        elo=elo,
        activities=json.dumps(activities),  # Store as JSON string
        resources_tlm=resources_tlm,
        worksheets=worksheets,
        assessment=assessment
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_sessions_by_lesson_id(db: Session, lesson_id: str) -> List[LessonSession]:
    """Get all sessions for a lesson"""
    return db.query(LessonSession).filter(
        LessonSession.lesson_id == lesson_id
    ).order_by(LessonSession.session_number).all()


def get_session_by_number(db: Session, lesson_id: str, session_number: int) -> Optional[LessonSession]:
    """Get specific session by number"""
    return db.query(LessonSession).filter(
        LessonSession.lesson_id == lesson_id,
        LessonSession.session_number == session_number
    ).first()


# ============ Statistics ============

def get_statistics(db: Session) -> dict:
    """Get database statistics"""
    total_transcripts = db.query(Transcript).count()
    total_lessons = db.query(LessonPlan).count()
    total_sessions = db.query(LessonSession).count()
    
    # Get subject distribution
    subjects = db.query(LessonPlan.subject, db.func.count(LessonPlan.subject)).group_by(
        LessonPlan.subject
    ).all()
    
    return {
        "total_transcripts": total_transcripts,
        "total_lessons": total_lessons,
        "total_sessions": total_sessions,
        "subjects_distribution": dict(subjects)
    }