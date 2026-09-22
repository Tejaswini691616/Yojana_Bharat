# PATH: GovScheme/models/scheme_model.py
from models.db import query, query_one, execute


def get_all_schemes():
    return query("SELECT * FROM schemes ORDER BY scheme_name")


def get_scheme_by_id(scheme_id: str):
    return query_one("SELECT * FROM schemes WHERE scheme_id = ?", (scheme_id,))


def search_schemes(keyword: str = "", category: str = "", state: str = ""):
    sql = "SELECT * FROM schemes WHERE 1=1"
    params = []
    if keyword:
        sql += " AND (LOWER(scheme_name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(eligibility) LIKE ?)"
        like = f"%{keyword.lower()}%"
        params += [like, like, like]
    if category:
        sql += " AND category = ?"
        params.append(category)
    if state:
        sql += " AND (state = ? OR state = 'All India')"
        params.append(state)
    sql += " ORDER BY scheme_name"
    return query(sql, tuple(params))


def get_categories_with_counts():
    return query("""
        SELECT category, COUNT(*) as scheme_count
        FROM schemes
        GROUP BY category
        ORDER BY category
    """)


def scheme_to_engine_dict(scheme_row: dict) -> dict:
    """The DB row already matches the field names ai/eligibility_engine.py expects."""
    return dict(scheme_row)
