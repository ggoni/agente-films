"""
Example usage of the database models for the multi-agent filmmaking system.

This demonstrates:
- Creating sessions and tracking ADK state
- Recording questions, reasoning, and answers
- Managing agent workflows
- Querying conversation history
- Performance monitoring
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, and_, desc, func
from sqlalchemy.orm import sessionmaker
from database.example_models import (
    Base, User, Session, Question, InferentialReasoning, Answer,
    Event, FilmProject, AgentTransfer, StateSnapshot,
    create_session, add_question, add_reasoning, add_answer,
    update_session_state, create_state_snapshot, get_conversation_context
)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/agente_films')
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


def example_1_create_user_and_session():
    """Example 1: Create a user and start an ADK session"""
    db = SessionLocal()

    try:
        # Create user
        user = User(
            email='filmmaker@example.com',
            username='filmmaker123',
            metadata={'preferences': {'theme': 'dark'}}
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user}")

        # Create ADK session
        session = create_session(
            db,
            user_id=str(user.id),
            session_name='Ancient Doctor Film Pitch',
            root_agent_name='greeter',
            agent_config={
                'model': 'gemini-2.5-flash',
                'agents': ['greeter', 'film_concept_team', 'writers_room']
            }
        )
        print(f"Created session: {session}")

        return user.id, session.id

    finally:
        db.close()


def example_2_record_conversation(user_id, session_id):
    """Example 2: Record a complete question-reasoning-answer flow"""
    db = SessionLocal()

    try:
        # User asks a question
        question = add_question(
            db,
            session_id=str(session_id),
            user_id=str(user_id),
            content="I want to create a film about an ancient doctor",
            sequence_number=1
        )
        print(f"Added question: {question}")

        # Agent 1: Researcher thinks and researches
        reasoning1 = add_reasoning(
            db,
            session_id=str(session_id),
            question_id=str(question.id),
            agent_name='researcher',
            reasoning_type='research',
            content='Searching for historical doctors... Found Zhang Zhongjing (150-219 CE), renowned Chinese physician.',
            sequence_number=1,
            state_delta={
                'research': ['Zhang Zhongjing was a Chinese physician during the Han Dynasty']
            }
        )
        print(f"Added reasoning: {reasoning1}")

        # Update session state with research
        update_session_state(
            db,
            session_id=str(session_id),
            state_updates={
                'research': ['Zhang Zhongjing was a Chinese physician during the Han Dynasty']
            }
        )

        # Agent 2: Screenwriter creates plot
        reasoning2 = add_reasoning(
            db,
            session_id=str(session_id),
            question_id=str(question.id),
            agent_name='screenwriter',
            reasoning_type='planning',
            content='Creating three-act structure based on research...',
            sequence_number=2,
            state_delta={
                'PLOT_OUTLINE': 'Act I: Young Zhang witnesses plague outbreak...'
            }
        )

        # Update session state with plot
        update_session_state(
            db,
            session_id=str(session_id),
            state_updates={
                'PLOT_OUTLINE': 'Act I: Young Zhang witnesses plague outbreak in his village...'
            }
        )

        # Agent 3: Critic reviews
        reasoning3 = add_reasoning(
            db,
            session_id=str(session_id),
            question_id=str(question.id),
            agent_name='critic',
            reasoning_type='critique',
            content='Plot outline needs more emotional depth in Act II',
            sequence_number=3,
            state_delta={
                'CRITICAL_FEEDBACK': 'Add more character development in Act II'
            }
        )

        # Final answer to user
        answer = add_answer(
            db,
            session_id=str(session_id),
            question_id=str(question.id),
            agent_name='file_writer',
            content="I've created a plot outline for a film about Zhang Zhongjing. The file has been saved to movie_pitches/The_Healing_Hands.txt",
            sequence_number=4,
            tokens_used=2500,
            response_time_ms=3200
        )
        print(f"Added answer: {answer}")

        return question.id

    finally:
        db.close()


def example_3_track_agent_transfers(session_id):
    """Example 3: Track agent workflow with transfers"""
    db = SessionLocal()

    try:
        # Record agent transfers
        transfers = [
            AgentTransfer(
                session_id=str(session_id),
                from_agent='greeter',
                to_agent='film_concept_team',
                transfer_reason='User provided historical subject'
            ),
            AgentTransfer(
                session_id=str(session_id),
                from_agent='film_concept_team',
                to_agent='writers_room',
                transfer_reason='Starting iterative writing process'
            ),
            AgentTransfer(
                session_id=str(session_id),
                from_agent='writers_room',
                to_agent='researcher',
                transfer_reason='Loop iteration 1: Research phase'
            )
        ]

        for transfer in transfers:
            db.add(transfer)

        db.commit()
        print(f"Recorded {len(transfers)} agent transfers")

        # Query transfer flow
        flow = db.query(AgentTransfer).filter(
            AgentTransfer.session_id == str(session_id)
        ).order_by(AgentTransfer.transferred_at).all()

        print("\nAgent Transfer Flow:")
        for t in flow:
            print(f"  {t.from_agent} → {t.to_agent}: {t.transfer_reason}")

    finally:
        db.close()


def example_4_create_film_project(session_id, user_id):
    """Example 4: Create film project from session"""
    db = SessionLocal()

    try:
        # Get final state from session
        session = db.query(Session).filter(Session.id == session_id).first()

        # Create film project
        film = FilmProject(
            session_id=str(session_id),
            user_id=str(user_id),
            title='The Healing Hands',
            historical_subject='Zhang Zhongjing',
            genre='Historical Drama',
            status='completed',
            plot_outline=session.state.get('PLOT_OUTLINE', ''),
            research_summary='\n'.join(session.state.get('research', [])),
            casting_report=session.state.get('casting_report', ''),
            box_office_report=session.state.get('box_office_report', ''),
            output_file_path='/path/to/movie_pitches/The_Healing_Hands.txt'
        )

        db.add(film)
        db.commit()
        db.refresh(film)
        print(f"Created film project: {film}")

        return film.id

    finally:
        db.close()


def example_5_create_state_snapshot(session_id):
    """Example 5: Create state snapshots for recovery"""
    db = SessionLocal()

    try:
        # Create snapshot after major milestone
        snapshot = create_state_snapshot(
            db,
            session_id=str(session_id),
            snapshot_type='checkpoint',
            description='After completing plot outline'
        )
        print(f"Created state snapshot: {snapshot}")

        # Later: Restore from snapshot
        latest_snapshot = db.query(StateSnapshot).filter(
            StateSnapshot.session_id == str(session_id)
        ).order_by(desc(StateSnapshot.created_at)).first()

        if latest_snapshot:
            print(f"\nLatest snapshot state: {latest_snapshot.state}")

    finally:
        db.close()


def example_6_query_conversation_context(session_id):
    """Example 6: Get complete conversation context"""
    db = SessionLocal()

    try:
        context = get_conversation_context(db, str(session_id))

        print("\n=== Complete Conversation Context ===")
        print(f"Session: {context['session_name']}")
        print(f"State: {context['state']}")
        print("\nConversation:")

        for turn in context['conversation']:
            print(f"\n  Q{turn['question']['sequence']}: {turn['question']['content']}")

            for reasoning in turn['reasoning']:
                print(f"    [{reasoning['agent']}] {reasoning['type']}: {reasoning['content'][:50]}...")

            for answer in turn['answers']:
                print(f"    A[{answer['agent']}]: {answer['content'][:50]}...")

    finally:
        db.close()


def example_7_analytics_queries(user_id):
    """Example 7: Analytics and performance queries"""
    db = SessionLocal()

    try:
        # User activity summary
        user_stats = db.query(
            func.count(Session.id).label('total_sessions'),
            func.sum(Session.total_events).label('total_events'),
            func.sum(Session.total_tokens_used).label('total_tokens')
        ).filter(Session.user_id == user_id).first()

        print("\n=== User Activity Summary ===")
        print(f"Total Sessions: {user_stats.total_sessions}")
        print(f"Total Events: {user_stats.total_events}")
        print(f"Total Tokens: {user_stats.total_tokens}")

        # Agent performance
        agent_perf = db.query(
            Answer.agent_name,
            func.count(Answer.id).label('responses'),
            func.avg(Answer.tokens_used).label('avg_tokens'),
            func.avg(Answer.response_time_ms).label('avg_response_time')
        ).group_by(Answer.agent_name).all()

        print("\n=== Agent Performance ===")
        for agent in agent_perf:
            print(f"{agent.agent_name}: {agent.responses} responses, "
                  f"avg {agent.avg_tokens:.0f} tokens, "
                  f"avg {agent.avg_response_time:.0f}ms")

        # Recent questions with full-text search
        search_term = 'ancient doctor'
        recent_questions = db.query(Question).filter(
            Question.content.ilike(f'%{search_term}%')
        ).order_by(desc(Question.asked_at)).limit(5).all()

        print(f"\n=== Questions matching '{search_term}' ===")
        for q in recent_questions:
            print(f"  {q.asked_at}: {q.content[:60]}...")

    finally:
        db.close()


def example_8_state_queries(session_id):
    """Example 8: Query JSONB state with PostgreSQL operators"""
    db = SessionLocal()

    try:
        # Find sessions with specific state key
        sessions_with_plot = db.query(Session).filter(
            Session.state.has_key('PLOT_OUTLINE')
        ).all()

        print("\n=== Sessions with PLOT_OUTLINE ===")
        for s in sessions_with_plot:
            print(f"  {s.session_name}: {s.state['PLOT_OUTLINE'][:50]}...")

        # Query by state value (containment)
        # Note: Use SQLAlchemy's JSONB operators
        from sqlalchemy.dialects.postgresql import JSONB

        sessions_with_research = db.query(Session).filter(
            Session.state['research'].astext.contains('Zhang')
        ).all()

        print("\n=== Sessions with Zhang in research ===")
        for s in sessions_with_research:
            print(f"  {s.session_name}")

    finally:
        db.close()


def example_9_partition_queries(session_id):
    """Example 9: Query partitioned events table"""
    db = SessionLocal()

    try:
        # Query events for specific session (partition pruning)
        events = db.query(Event).filter(
            and_(
                Event.session_id == session_id,
                Event.created_at >= datetime(2025, 1, 1)
            )
        ).order_by(Event.created_at).all()

        print("\n=== Session Events (Jan 2025) ===")
        for e in events:
            print(f"  {e.created_at}: {e.event_type} - {e.agent_name}")

        # Query tool calls only
        tool_calls = db.query(Event).filter(
            and_(
                Event.session_id == session_id,
                Event.event_type == 'tool_call'
            )
        ).all()

        print(f"\nTotal tool calls: {len(tool_calls)}")
        for tc in tool_calls:
            print(f"  {tc.tool_name}: {tc.tool_input}")

    finally:
        db.close()


def example_10_complete_workflow():
    """Example 10: Complete end-to-end workflow"""
    print("=== Starting Complete Workflow ===\n")

    # 1. Create user and session
    user_id, session_id = example_1_create_user_and_session()

    # 2. Record conversation
    question_id = example_2_record_conversation(user_id, session_id)

    # 3. Track agent transfers
    example_3_track_agent_transfers(session_id)

    # 4. Create film project
    film_id = example_4_create_film_project(session_id, user_id)

    # 5. Create snapshots
    example_5_create_state_snapshot(session_id)

    # 6. Query conversation
    example_6_query_conversation_context(session_id)

    # 7. Analytics
    example_7_analytics_queries(user_id)

    # 8. State queries
    example_8_state_queries(session_id)

    # 9. Partition queries
    example_9_partition_queries(session_id)

    print("\n=== Workflow Complete ===")
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")
    print(f"Film Project ID: {film_id}")


if __name__ == '__main__':
    # Run examples
    print("Database Examples for Multi-Agent Filmmaking System\n")

    # Run complete workflow
    example_10_complete_workflow()

    # Or run individual examples:
    # user_id, session_id = example_1_create_user_and_session()
    # example_2_record_conversation(user_id, session_id)
    # etc.
