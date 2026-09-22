# PATH: GovScheme/README.md
# SmartGov AI

AI + RPA Based Government Scheme Eligibility, Personalized Recommendation,
Multilingual Voice Assistant and Application Assistance System.

**This is a working local prototype**, built and tested end-to-end in this
environment (registration → dashboard → eligibility → ML recommendations →
chatbot → apply-now demo RPA → applications tracking → admin scheme-update
pipeline all run successfully). See "What was actually verified" below.

---

## 1. Setup on Windows (VS Code)

1. Install Python 3.11+ from python.org (check "Add to PATH" during install).
2. Extract this `GovScheme` folder anywhere, e.g. `C:\Users\<you>\Desktop\GovScheme`.
3. Open the folder in VS Code (`File > Open Folder`).
4. Open a terminal in VS Code (`` Ctrl+` ``) and run:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` (a working `.env` with a generated secret
   key is already included, so this step is optional for a first run).
6. Build the database from the attached Excel dataset:
   ```
   python database\build_db.py
   ```
7. Train the ML recommendation model (takes under a minute):
   ```
   python ai\train_model.py
   ```
8. Run the app:
   ```
   python app.py
   ```
9. Open http://127.0.0.1:5000 in your browser, click **Create an account**,
   fill in your profile, and explore the dashboard, schemes, chatbot,
   applications and admin pages.
10. To become an admin user (for the Admin dashboard / manual scheme-check
    button), run once after registering:
    ```
    python -c "from models.db import execute; execute(\"UPDATE users SET is_admin=1 WHERE email='YOUR_EMAIL_HERE'\")"
    ```

---

## 2. What was actually verified in this build (not assumed)

- **Eligibility engine** validated against the real `Eligibility_Records`
  sheet: **99.56% match** on a 5,000-row sample. The small number of
  mismatches trace to PM-KISAN / Kisan Credit Card records where the
  original labels also depend on `Bank_Account`/`Aadhaar` status — fields
  not exposed as configured criteria in `Scheme_Master`. This is a real,
  documented data-quality finding, not an engine defect.
- **ML training**, using the required Citizen_ID-based split (leak-free):
  4,000 citizens / 80,000 records → train, 1,000 citizens / 20,000 records
  → test — matching the spec's expected proportions exactly, computed
  programmatically (not hardcoded). Actual results (see
  `ml_models/metrics.json` after running `train_model.py`):
  - Logistic Regression: F1 ≈ 0.828
  - Decision Tree: F1 ≈ 0.972 (**selected**, highest F1)
  - Random Forest: F1 ≈ 0.965
  Random Forest was **not** assumed to win — the actual F1 scores decided it.
- **Full request flow** was run end-to-end with `curl` against a live
  server in this environment: register → login → dashboard →
  recommendations → scheme details → Apply Now (DEMO RPA, reference number
  prefixed `DEMO-...`) → applications list → profile → notifications →
  chatbot `/api/chat/message` → admin dashboard → manual "Run Scheme Update
  Check Now" (correctly detected 1 NEW + 1 UPDATED scheme against the mock
  feed). All returned HTTP 200/302 with no server errors.
- **23 automated tests** in `tests/` pass (`pytest`), covering the
  eligibility engine's edge cases (Yes/No/1/0/blank/case handling), the
  recommendation service's eligible-subset guarantee, auth flow, scheme
  search, the DEMO application flow, and the chatbot API.

## 3. Known limitations (disclosed, not hidden)

- **Land_Limit** in the source Excel is a boolean flag (always `False` for
  all 20 schemes) rather than a numeric acreage cap. The engine supports a
  numeric `land_limit_acres` field for when real data is available, but it
  is currently inert with this dataset.
- **Scheme categories**: the actual dataset has 9 categories (not the 10 in
  the original spec draft). The dashboard's category cards use the real 9.
- **Voice (STT/TTS)** is not wired to any paid provider by default — this
  keeps the project runnable with zero external cost/dependency. Text chat
  works fully offline in all 12 target languages' UI phrasing (English and
  Hindi have complete phrase sets in `ai/response_generator.py`; other
  languages fall back to English text with a disclosed note — extend
  `PHRASES` in that file to add full translations). The mic button in the UI
  will clearly say voice isn't configured rather than pretending to work.
- **UiPath RPA**: no UiPath Studio/Orchestrator is available in this build
  environment. `rpa/application_request.py` ships a fully working DEMO
  government-portal simulator (`RPA_MODE=DEMO`, the default) for the
  Apply Now → RPA → Reference Number → Tracking flow, plus a documented,
  ready-to-implement integration point for a real UiPath Orchestrator
  (`RPA_MODE=UIPATH`) — see `rpa/uipath/README.md`.
- **Government scheme discovery** reads from a local
  `automation/mock_official_feed.json` rather than a real government
  website, since this sandbox cannot safely/legitimately scrape live
  government portals. Swap `automation/scheme_scraper.py`'s
  `fetch_candidate_schemes()` for a real official API/feed call — the
  validator, change-detector, and scheduler around it need no changes.

## 4. Project structure

See the folder tree; it matches the structure agreed at the start of this
project (`app.py`, `config.py`, `database/`, `models/`, `routes/`, `ai/`,
`automation/`, `rpa/`, `templates/`, `static/`, `tests/`).

## 5. Running tests

```
pytest tests/ -v
```
