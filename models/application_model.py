# PATH: GovScheme/models/application_model.py
from models.db import query, query_one, execute


def create_application(user_id: int, scheme_id: str) -> int:
    return execute("""
        INSERT INTO applications (user_id, scheme_id, status)
        VALUES (?, ?, 'Draft')
    """, (user_id, scheme_id))


def get_application(application_id: int):
    return query_one("""
        SELECT a.*, s.scheme_name FROM applications a
        JOIN schemes s ON a.scheme_id = s.scheme_id
        WHERE a.application_id = ?
    """, (application_id,))


def get_applications_for_user(user_id: int):
    return query("""
        SELECT a.*, s.scheme_name FROM applications a
        JOIN schemes s ON a.scheme_id = s.scheme_id
        WHERE a.user_id = ?
        ORDER BY a.created_at DESC
    """, (user_id,))


def update_application_status(application_id: int, status: str, application_number: str = None, remarks: str = None):
    execute("""
        UPDATE applications
        SET status = ?, application_number = COALESCE(?, application_number),
            remarks = COALESCE(?, remarks), updated_at = datetime('now')
        WHERE application_id = ?
    """, (status, application_number, remarks, application_id))
