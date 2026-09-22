# PATH: GovScheme/rpa/uipath/README.md

## UiPath integration (real RPA path)

This folder is where a real UiPath Studio project (`.xaml` workflows) would
live for the "Open portal -> Navigate -> Enter repetitive info -> Upload
documents -> Submit -> Read reference number" flow described in the spec.

Because this environment does not have UiPath Studio/Robot/Orchestrator
installed, no `.xaml` workflow is included here. To complete the real RPA
path on your Windows machine:

1. Install UiPath Studio Community Edition.
2. Create a new process, e.g. `SubmitSchemeApplication.xaml`, that:
   - Opens the target portal (only where automation is permitted by the
     portal's terms of use).
   - Fills the repetitive fields from `application_id`'s structured input.
   - Uploads permitted documents.
   - Submits where permitted, or stops and flags `Needs Manual Action`
     if a CAPTCHA/OTP/biometric/login control is encountered — **never
     automate around these** (spec section 56).
   - Reads back the application reference number.
2. Publish the process to Orchestrator (or run it locally with UiPath
   Robot for a demo).
3. In `.env`, set:
   ```
   RPA_MODE=UIPATH
   UIPATH_ORCHESTRATOR_URL=https://your-orchestrator-url
   UIPATH_ORCHESTRATOR_TENANT=...
   UIPATH_ORCHESTRATOR_CLIENT_ID=...
   UIPATH_ORCHESTRATOR_CLIENT_SECRET=...
   ```
4. Implement `_run_via_uipath_orchestrator()` in
   `GovScheme/rpa/application_request.py` to call your Orchestrator's
   REST API (start job, poll status, return the reference number).

Until then, leave `RPA_MODE=DEMO` in `.env` — the built-in DEMO portal
simulator in `application_request.py` lets you demonstrate the full
Apply Now -> RPA -> Reference Number -> Tracking flow end-to-end without
any external dependency, with every generated number clearly prefixed
`DEMO-`.
