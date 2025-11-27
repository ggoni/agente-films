"""
SQLAlchemy ORM models for the multi-agent filmmaking system.

Usage:
    from database.example_models import Session, FilmProject, Event
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('postgresql://user:pass@localhost/agente_films')
    SessionLocal = sessionmaker(bind=engine)

    db = SessionLocal()
    session = db.query(Session).filter(Session.id == session_id).first()
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(100), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    metadata = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)

    # Relationships
    sessions = relationship('Session', back_populates='user', cascade='all, delete-orphan')
    film_projects = relationship('FilmProject', back_populates='user', cascade='all, delete-orphan')
    questions = relationship('Question', back_populates='user', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_active', 'is_active', postgresql_where=(is_active)),
        Index('idx_users_created_at', 'created_at', postgresql_using='btree', postgresql_ops={'created_at': 'DESC'}),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    session_name = Column(String(255))
    started_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    ended_at = Column(TIMESTAMP(timezone=True))

    # ADK state
    state = Column(JSONB, nullable=False, default={})
    root_agent_name = Column(String(100))
    agent_config = Column(JSONB)

    # Status
    status = Column(
        String(50),
        default='active',
        nullable=False
    )

    # Performance metrics
    total_events = Column(Integer, default=0)
    total_tool_calls = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)

    # Metadata
    metadata = Column(JSONB, default={})

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='sessions')
    questions = relationship('Question', back_populates='session', cascade='all, delete-orphan')
    answers = relationship('Answer', back_populates='session', cascade='all, delete-orphan')
    events = relationship('Event', back_populates='session', cascade='all, delete-orphan')
    film_projects = relationship('FilmProject', back_populates='session', cascade='all, delete-orphan')
    agent_transfers = relationship('AgentTransfer', back_populates='session', cascade='all, delete-orphan')
    state_snapshots = relationship('StateSnapshot', back_populates='session', cascade='all, delete-orphan')
    reasoning_events = relationship('InferentialReasoning', back_populates='session', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint("status IN ('active', 'completed', 'failed', 'archived')", name='sessions_status_check'),
        Index('idx_sessions_user_id', 'user_id'),
        Index('idx_sessions_status', 'status'),
        Index('idx_sessions_started_at', 'started_at', postgresql_ops={'started_at': 'DESC'}),
        Index('idx_sessions_user_started', 'user_id', 'started_at', postgresql_ops={'started_at': 'DESC'}),
        Index('idx_sessions_active', 'status', 'started_at',
              postgresql_where=(status == 'active'),
              postgresql_ops={'started_at': 'DESC'}),
        Index('idx_sessions_state', 'state', postgresql_using='gin', postgresql_ops={'state': 'jsonb_path_ops'}),
        Index('idx_sessions_metadata', 'metadata', postgresql_using='gin', postgresql_ops={'metadata': 'jsonb_path_ops'}),
    )

    def __repr__(self):
        return f"<Session(id={self.id}, name='{self.session_name}', status='{self.status}')>"

    @property
    def duration_seconds(self) -> float | None:
        """Calculate session duration in seconds"""
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return (datetime.utcnow() - self.started_at).total_seconds()


class FilmProject(Base):
    __tablename__ = 'film_projects'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))

    # Film details
    title = Column(String(500))
    historical_subject = Column(String(500))
    genre = Column(String(100))

    # Status
    status = Column(String(50), default='draft')

    # Content (denormalized from state)
    plot_outline = Column(Text)
    research_summary = Column(Text)
    casting_report = Column(Text)
    box_office_report = Column(Text)

    # File reference
    output_file_path = Column(Text)

    # Metadata
    metadata = Column(JSONB, default={})

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    session = relationship('Session', back_populates='film_projects')
    user = relationship('User', back_populates='film_projects')

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'in_progress', 'completed', 'archived')", name='film_projects_status_check'),
        Index('idx_film_projects_session_id', 'session_id'),
        Index('idx_film_projects_user_id', 'user_id'),
        Index('idx_film_projects_status', 'status'),
        Index('idx_film_projects_created_at', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_film_projects_title_trgm', 'title', postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'}),
        Index('idx_film_projects_subject_trgm', 'historical_subject', postgresql_using='gin',
              postgresql_ops={'historical_subject': 'gin_trgm_ops'}),
    )

    def __repr__(self):
        return f"<FilmProject(id={self.id}, title='{self.title}', status='{self.status}')>"


class Question(Base):
    __tablename__ = 'questions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Content
    content = Column(Text, nullable=False)
    context = Column(JSONB, default={})

    # Sequencing
    sequence_number = Column(Integer, nullable=False)

    # Timing
    asked_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Metadata
    metadata = Column(JSONB, default={})

    # Relationships
    session = relationship('Session', back_populates='questions')
    user = relationship('User', back_populates='questions')
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')
    reasoning_events = relationship('InferentialReasoning', back_populates='question', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_questions_session_id', 'session_id', 'sequence_number'),
        Index('idx_questions_user_id', 'user_id'),
        Index('idx_questions_asked_at', 'asked_at', postgresql_ops={'asked_at': 'DESC'}),
        Index('idx_questions_content_trgm', 'content', postgresql_using='gin', postgresql_ops={'content': 'gin_trgm_ops'}),
    )

    def __repr__(self):
        return f"<Question(id={self.id}, sequence={self.sequence_number})>"


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE'))

    # Content
    content = Column(Text, nullable=False)

    # Agent info
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(100))

    # Sequencing
    sequence_number = Column(Integer, nullable=False)

    # Performance
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)

    # Timing
    answered_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Metadata
    metadata = Column(JSONB, default={})

    # Relationships
    session = relationship('Session', back_populates='answers')
    question = relationship('Question', back_populates='answers')
    reasoning_events = relationship('InferentialReasoning', back_populates='answer', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_answers_session_id', 'session_id', 'sequence_number'),
        Index('idx_answers_question_id', 'question_id'),
        Index('idx_answers_agent_name', 'agent_name'),
        Index('idx_answers_answered_at', 'answered_at', postgresql_ops={'answered_at': 'DESC'}),
        Index('idx_answers_content_trgm', 'content', postgresql_using='gin', postgresql_ops={'content': 'gin_trgm_ops'}),
    )

    def __repr__(self):
        return f"<Answer(id={self.id}, agent='{self.agent_name}', sequence={self.sequence_number})>"


class InferentialReasoning(Base):
    __tablename__ = 'inferential_reasoning'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE'))
    answer_id = Column(UUID(as_uuid=True), ForeignKey('answers.id', ondelete='CASCADE'))

    # Agent info
    agent_name = Column(String(100), nullable=False)
    agent_role = Column(String(200))

    # Reasoning
    reasoning_type = Column(String(100))
    content = Column(Text, nullable=False)

    # State changes
    state_delta = Column(JSONB)

    # Sequencing
    sequence_number = Column(Integer, nullable=False)

    # Timing
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Metadata
    metadata = Column(JSONB, default={})

    # Relationships
    session = relationship('Session', back_populates='reasoning_events')
    question = relationship('Question', back_populates='reasoning_events')
    answer = relationship('Answer', back_populates='reasoning_events')

    __table_args__ = (
        CheckConstraint(
            "reasoning_type IN ('research', 'planning', 'critique', 'analysis', 'decision', 'other')",
            name='inferential_reasoning_type_check'
        ),
        Index('idx_reasoning_session_id', 'session_id', 'sequence_number'),
        Index('idx_reasoning_question_id', 'question_id'),
        Index('idx_reasoning_answer_id', 'answer_id'),
        Index('idx_reasoning_agent', 'agent_name'),
        Index('idx_reasoning_type', 'reasoning_type'),
        Index('idx_reasoning_created_at', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_reasoning_state_delta', 'state_delta', postgresql_using='gin',
              postgresql_ops={'state_delta': 'jsonb_path_ops'}),
    )

    def __repr__(self):
        return f"<InferentialReasoning(id={self.id}, type='{self.reasoning_type}', agent='{self.agent_name}')>"


class Event(Base):
    """
    Note: This is a base model for the partitioned events table.
    In practice, you'll interact with specific partitions (events_2025_01, etc.)
    """
    __tablename__ = 'events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)

    # Event type
    event_type = Column(String(100), nullable=False)

    # Agent context
    agent_name = Column(String(100))
    parent_agent_name = Column(String(100))

    # Event details
    event_data = Column(JSONB, nullable=False)

    # Tool information
    tool_name = Column(String(100))
    tool_input = Column(JSONB)
    tool_output = Column(JSONB)

    # State changes
    state_delta = Column(JSONB)

    # Performance
    duration_ms = Column(Integer)
    tokens_used = Column(Integer)

    # Error tracking
    error_message = Column(Text)

    # Timing
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Metadata
    metadata = Column(JSONB, default={})

    # Relationships
    session = relationship('Session', back_populates='events')

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('user_message', 'agent_response', 'tool_call', 'tool_response', " +
            "'agent_transfer', 'state_update', 'loop_iteration', 'error', 'other')",
            name='events_type_check'
        ),
        Index('idx_events_session_id', 'session_id', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_events_type', 'event_type', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_events_agent', 'agent_name', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_events_tool', 'tool_name', postgresql_where=(tool_name is not None)),
        Index('idx_events_data', 'event_data', postgresql_using='gin', postgresql_ops={'event_data': 'jsonb_path_ops'}),
        Index('idx_events_state_delta', 'state_delta', postgresql_using='gin',
              postgresql_ops={'state_delta': 'jsonb_path_ops'}),
    )

    def __repr__(self):
        return f"<Event(id={self.id}, type='{self.event_type}', agent='{self.agent_name}')>"


class AgentTransfer(Base):
    __tablename__ = 'agent_transfers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(UUID(as_uuid=True))

    # Transfer details
    from_agent = Column(String(100), nullable=False)
    to_agent = Column(String(100), nullable=False)
    transfer_reason = Column(Text)

    # Timing
    transferred_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Metadata
    metadata = Column(JSONB, default={})

    # Relationships
    session = relationship('Session', back_populates='agent_transfers')

    __table_args__ = (
        Index('idx_transfers_session_id', 'session_id', 'transferred_at',
              postgresql_ops={'transferred_at': 'DESC'}),
        Index('idx_transfers_from_agent', 'from_agent'),
        Index('idx_transfers_to_agent', 'to_agent'),
    )

    def __repr__(self):
        return f"<AgentTransfer(id={self.id}, from='{self.from_agent}', to='{self.to_agent}')>"


class StateSnapshot(Base):
    __tablename__ = 'state_snapshots'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)

    # Snapshot details
    snapshot_type = Column(String(50))
    state = Column(JSONB, nullable=False)
    event_sequence_number = Column(Integer)

    # Timing
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Metadata
    description = Column(Text)
    metadata = Column(JSONB, default={})

    # Relationships
    session = relationship('Session', back_populates='state_snapshots')

    __table_args__ = (
        CheckConstraint("snapshot_type IN ('manual', 'automatic', 'checkpoint')", name='snapshot_type_check'),
        Index('idx_snapshots_session_id', 'session_id', 'created_at', postgresql_ops={'created_at': 'DESC'}),
        Index('idx_snapshots_type', 'snapshot_type'),
        Index('idx_snapshots_state', 'state', postgresql_using='gin', postgresql_ops={'state': 'jsonb_path_ops'}),
    )

    def __repr__(self):
        return f"<StateSnapshot(id={self.id}, type='{self.snapshot_type}')>"


class SystemConfig(Base):
    __tablename__ = 'system_config'

    key = Column(String(100), primary_key=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value={self.value})>"


# Helper functions for working with models

def create_session(
    db,
    user_id: str,
    session_name: str,
    root_agent_name: str,
    agent_config: dict[str, Any]
) -> Session:
    """Create a new ADK session"""
    session = Session(
        user_id=user_id,
        session_name=session_name,
        root_agent_name=root_agent_name,
        agent_config=agent_config,
        state={},
        status='active'
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def add_question(
    db,
    session_id: str,
    user_id: str,
    content: str,
    sequence_number: int,
    context: dict[str, Any] | None = None
) -> Question:
    """Add a user question to the session"""
    question = Question(
        session_id=session_id,
        user_id=user_id,
        content=content,
        sequence_number=sequence_number,
        context=context or {}
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def add_reasoning(
    db,
    session_id: str,
    agent_name: str,
    content: str,
    sequence_number: int,
    reasoning_type: str = 'other',
    question_id: str | None = None,
    answer_id: str | None = None,
    state_delta: dict[str, Any] | None = None
) -> InferentialReasoning:
    """Add agent reasoning/thinking event"""
    reasoning = InferentialReasoning(
        session_id=session_id,
        question_id=question_id,
        answer_id=answer_id,
        agent_name=agent_name,
        reasoning_type=reasoning_type,
        content=content,
        sequence_number=sequence_number,
        state_delta=state_delta
    )
    db.add(reasoning)
    db.commit()
    db.refresh(reasoning)
    return reasoning


def add_answer(
    db,
    session_id: str,
    agent_name: str,
    content: str,
    sequence_number: int,
    question_id: str | None = None,
    tokens_used: int | None = None,
    response_time_ms: int | None = None
) -> Answer:
    """Add agent answer to the session"""
    answer = Answer(
        session_id=session_id,
        question_id=question_id,
        agent_name=agent_name,
        content=content,
        sequence_number=sequence_number,
        tokens_used=tokens_used,
        response_time_ms=response_time_ms
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


def update_session_state(
    db,
    session_id: str,
    state_updates: dict[str, Any]
) -> Session:
    """Update session state dictionary"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if session:
        # Merge state updates
        current_state = session.state or {}
        current_state.update(state_updates)
        session.state = current_state
        db.commit()
        db.refresh(session)
    return session


def create_state_snapshot(
    db,
    session_id: str,
    snapshot_type: str = 'manual',
    description: str | None = None
) -> StateSnapshot:
    """Create a point-in-time state snapshot"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise ValueError(f"Session {session_id} not found")

    snapshot = StateSnapshot(
        session_id=session_id,
        snapshot_type=snapshot_type,
        state=session.state,
        description=description
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_conversation_context(db, session_id: str) -> dict[str, Any]:
    """Get complete conversation context for a session"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        return {}

    questions = db.query(Question).filter(
        Question.session_id == session_id
    ).order_by(Question.sequence_number).all()

    conversation = []
    for question in questions:
        # Get reasoning for this question
        reasoning = db.query(InferentialReasoning).filter(
            InferentialReasoning.question_id == question.id
        ).order_by(InferentialReasoning.sequence_number).all()

        # Get answers for this question
        answers = db.query(Answer).filter(
            Answer.question_id == question.id
        ).order_by(Answer.sequence_number).all()

        conversation.append({
            'question': {
                'id': str(question.id),
                'content': question.content,
                'sequence': question.sequence_number,
                'asked_at': question.asked_at.isoformat()
            },
            'reasoning': [
                {
                    'agent': r.agent_name,
                    'type': r.reasoning_type,
                    'content': r.content,
                    'state_delta': r.state_delta
                }
                for r in reasoning
            ],
            'answers': [
                {
                    'id': str(a.id),
                    'agent': a.agent_name,
                    'content': a.content,
                    'tokens': a.tokens_used,
                    'answered_at': a.answered_at.isoformat()
                }
                for a in answers
            ]
        })

    return {
        'session_id': str(session.id),
        'session_name': session.session_name,
        'state': session.state,
        'agent_config': session.agent_config,
        'conversation': conversation
    }
