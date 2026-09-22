# PATH: GovScheme/database/build_db.py
"""
Builds SmartGov_AI.db from schema.sql and loads Scheme_Master from the
attached Excel workbook into the `schemes` table.

Citizen_Profile / Eligibility_Records from the Excel are SYNTHETIC ML
TRAINING DATA (5,000 fake citizens) - they are NOT loaded as `users`,
because `users` represents real people who register through the app.
Instead, ai/train_model.py reads the Excel directly for training.

Run:
    python database/build_db.py
"""
import os
import sqlite3
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


def _bool_from_excel(val) -> int:
    """Excel Farmer_Required etc. columns are already Python bool via pandas."""
    if pd.isna(val):
        return 0
    return 1 if bool(val) else 0


def build_database():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(Config.DATABASE_PATH)
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    if not os.path.exists(Config.EXCEL_SOURCE_PATH):
        print(f"WARNING: Excel source not found at {Config.EXCEL_SOURCE_PATH}. "
              f"Skipping scheme import.")
        conn.close()
        return

    sm = pd.read_excel(Config.EXCEL_SOURCE_PATH, sheet_name="Scheme_Master")

    cur = conn.cursor()
    inserted, updated = 0, 0
    for _, row in sm.iterrows():
        scheme_id = str(row["Scheme_ID"]).strip()
        scheme_name = str(row["Scheme_Name"]).strip()
        category = str(row["Category"]).strip() if pd.notna(row["Category"]) else None
        min_age = float(row["Min_Age"]) if pd.notna(row["Min_Age"]) else None
        max_age = float(row["Max_Age"]) if pd.notna(row["Max_Age"]) else None
        income_limit = float(row["Income_Limit"]) if pd.notna(row["Income_Limit"]) else None
        caste_req = str(row["Caste_Requirement"]).strip() if pd.notna(row["Caste_Requirement"]) else None
        farmer_required = _bool_from_excel(row["Farmer_Required"])
        bpl_required = _bool_from_excel(row["BPL_Required"])
        # NOTE (data quality): Land_Limit in the source workbook is a boolean flag
        # (always False for all 20 schemes), not a numeric acreage cap. We store it
        # as land_limit_required; land_limit_acres stays NULL since no numeric cap
        # exists in the current dataset. See dataset validation report.
        land_limit_required = _bool_from_excel(row["Land_Limit"])
        disability_required = _bool_from_excel(row["Disability_Required"])
        student_required = _bool_from_excel(row["Student_Required"])
        widow_required = _bool_from_excel(row["Widow_Required"])

        description = f"{scheme_name} is a {category} scheme configured in the SmartGov AI prototype dataset."
        eligibility_text_parts = []
        if min_age is not None:
            eligibility_text_parts.append(f"Minimum age {int(min_age)}")
        if max_age is not None:
            eligibility_text_parts.append(f"Maximum age {int(max_age)}")
        if income_limit is not None:
            eligibility_text_parts.append(f"Annual family income up to ₹{int(income_limit):,}")
        if caste_req:
            eligibility_text_parts.append(f"Caste category: {caste_req}")
        if farmer_required:
            eligibility_text_parts.append("Applicant must be a farmer")
        if bpl_required:
            eligibility_text_parts.append("Applicant must hold BPL status")
        if disability_required:
            eligibility_text_parts.append("Applicant must have a registered disability")
        if student_required:
            eligibility_text_parts.append("Applicant must be a student")
        if widow_required:
            eligibility_text_parts.append("Applicant must be a widow")
        eligibility_text = "; ".join(eligibility_text_parts) if eligibility_text_parts else \
            "No specific demographic criteria configured for this prototype scheme."

        cur.execute("""
            INSERT INTO schemes (
                scheme_id, scheme_name, category, description, benefits, eligibility,
                documents_required, official_link, application_link, state, status,
                source_url, last_checked, last_updated, verification_status,
                min_age, max_age, income_limit, caste_requirement,
                farmer_required, bpl_required, land_limit_required, land_limit_acres,
                disability_required, student_required, widow_required
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(scheme_id) DO UPDATE SET
                scheme_name=excluded.scheme_name,
                category=excluded.category,
                eligibility=excluded.eligibility,
                min_age=excluded.min_age,
                max_age=excluded.max_age,
                income_limit=excluded.income_limit,
                caste_requirement=excluded.caste_requirement,
                farmer_required=excluded.farmer_required,
                bpl_required=excluded.bpl_required,
                land_limit_required=excluded.land_limit_required,
                disability_required=excluded.disability_required,
                student_required=excluded.student_required,
                widow_required=excluded.widow_required,
                last_updated=datetime('now')
        """, (
            scheme_id, scheme_name, category, description, None, eligibility_text,
            None, None, None, "All India", "Active",
            "Local prototype dataset (Government_Scheme_Eligibility_Upgraded.xlsx)",
            "Verified (prototype dataset)",
            min_age, max_age, income_limit, caste_req,
            farmer_required, bpl_required, land_limit_required, None,
            disability_required, student_required, widow_required
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"Database built at {Config.DATABASE_PATH}")
    print(f"Schemes loaded/updated: {inserted}")


if __name__ == "__main__":
    build_database()
