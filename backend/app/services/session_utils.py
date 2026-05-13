from datetime import datetime, timezone

def check_session_expired(session, db):
    now = datetime.now(timezone.utc)

    if session.finished_at is None and session.end_time and now > session.end_time:
        session.finished_at = now
        db.commit()
        return True

    return False
