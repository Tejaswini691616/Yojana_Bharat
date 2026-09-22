# PATH: GovScheme/models/user_model.py
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import query, query_one, execute


def create_user(data: dict) -> int:
    password_hash = generate_password_hash(data["password"])
    return execute("""
        INSERT INTO users (full_name, email, password_hash, phone, gender, age, state,
            district, education, occupation, annual_income, caste, farmer, student,
            disabled, senior_citizen, bpl, widow, land_holding_acres, preferred_language)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("full_name"), data.get("email"), password_hash, data.get("phone"),
        data.get("gender"), data.get("age"), data.get("state"), data.get("district"),
        data.get("education"), data.get("occupation"), data.get("annual_income"),
        data.get("caste"), data.get("farmer", "No"), data.get("student", "No"),
        data.get("disabled", "No"), data.get("senior_citizen", "No"),
        data.get("bpl", "No"), data.get("widow", "No"),
        data.get("land_holding_acres", 0), data.get("preferred_language", "English"),
    ))


def get_user_by_email(email: str):
    return query_one("SELECT * FROM users WHERE email = ?", (email,))


def get_user_by_id(user_id: int):
    return query_one("SELECT * FROM users WHERE user_id = ?", (user_id,))


def verify_password(user_row, password: str) -> bool:
    return check_password_hash(user_row["password_hash"], password)


def update_user_profile(user_id: int, data: dict):
    fields = ["full_name", "phone", "gender", "age", "state", "district", "education",
              "occupation", "annual_income", "caste", "farmer", "student", "disabled",
              "senior_citizen", "bpl", "widow", "land_holding_acres", "preferred_language"]
    set_clause = ", ".join(f"{f} = ?" for f in fields if f in data)
    values = [data[f] for f in fields if f in data]
    if not set_clause:
        return
    values.append(user_id)
    execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", tuple(values))


def citizen_dict_for_engine(user_row: dict) -> dict:
    """Adapt a `users` row to the shape expected by ai/eligibility_engine.py."""
    return {
        "age": user_row.get("age"),
        "annual_family_income": user_row.get("annual_income"),
        "caste": user_row.get("caste"),
        "farmer": user_row.get("farmer"),
        "bpl": user_row.get("bpl"),
        "disability": user_row.get("disabled"),
        "student": user_row.get("student"),
        "widow": user_row.get("widow"),
        "land_holding_acres": user_row.get("land_holding_acres"),
    }
