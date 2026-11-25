# Type Camp — AI working context

## Maintain this file

Read this file at the start of repository work, then inspect the relevant code and Git status. Update it in the same change whenever behavior, decisions, commands, verified issues, or next steps change. Remove resolved issues and superseded plans. Date verification results and distinguish implemented behavior from proposed work. Keep this concise and actionable; use README.md for public setup instructions. Never record secrets, recovery phrases, or personal data here.

## Current state

- Mobile-first Pokémon GO type-effectiveness trainer. Django 5.2 LTS, SQLite, server-rendered templates, plain browser JavaScript. User hosts on an Ubuntu VPS and dislikes Node/npm.
- Routes are practice at `/`, the move-type reference at `/chart/`, and progress/recovery at `/progress/`.
- Ten answers per calendar day complete the daily goal. Unlimited continuation, immediate feedback, “I don’t know,” and persisted answers are implemented.
- Guided progression starts with Water/Fire/Grass. Every 10 lifetime correct answers unlocks one single type (all 18 at 150), then one dual combination (first at 160), up to the bundled 139 released GO combinations. The menu also offers immediate all-single and all-dual practice. Questions ask for effectiveness or the strongest move among supplied choices.
- Automatic anonymous profiles use a signed UUID cookie. Optional nine-name Pokémon recovery phrases connect devices to the same profile. Existing practice history triggers confirmation before restoration. The current product scope excludes login and a switch-trainer menu.
- GitHub is `jusasiiv/Type-Camp`, branch `trunk`. Check tracking configuration before pulling/pushing. README’s prominent fully-AI-coded, human-unreviewed disclaimer is an explicit user requirement.

## Decisions and reasons

- **GO rules are authoritative.** `trainer/rules.py` represents matchups as exponents of 1.6 and uses Decimal for display. Single-type factors are 1.6, 1, 0.625, and 0.390625. Add exponents for dual types, yielding values including 2.56 and 0.244140625. Identify the attacking move and defending types explicitly. Scope is type effectiveness only.
- **Retrieval, feedback, and spacing guide learning.** Missed answers become eligible for retry after two intervening answers and are due tomorrow. New matchups are also due tomorrow. Correct recall on a later due day triples the interval up to 60 days; same-day repetition cannot increase it. This schedule and the ten-question goal are implementation choices based on the research principles linked in README.
- **Unlocks use saved correct answers.** All modes and earlier history count; mistakes never remove progress. `progression.py` derives unlocks without another stored counter. Guided practice includes unlocked move types, single defenders, and dual defenders; new questions favor the latest unlock after missed/due reviews. Migration 0003 converts starter profiles while preserving their active questions, attempts, reviews, and existing single/dual selections.
- **Dual coverage is a dated GO snapshot.** `dual_types.py` contains 139 unordered pairs from PvPoke's released roster, checked 2026-11-25, including regional forms and Megas. Its pinned source is in the file and README. Append future pairs; preserve unlock order and legacy type ordering so stored matchup keys remain valid. New examples without bundled sprites use the type-orb fallback.
- **Python owns correctness and scheduling.** JavaScript submits forms and replaces the lesson fragment for smooth interaction. Ordinary POST/redirect forms support the same flow. This keeps deployment simple and avoids duplicated rules.
- **Persistence handles retries.** `Trainer` stores the shared current question; `Attempt.token` is unique; `Review` is unique per trainer/matchup. Atomic views and SQLite IMMEDIATE transactions serialize writes. Preserve duplicate-submit protection when changing the flow.
- **Recovery is a bearer credential.** Names come from `secrets.choice`; only the SHA-256 fingerprint is stored. Normalization accepts case changes, whitespace, and hyphens. Plaintext appears once. Replacement invalidates the old phrase; existing cookies keep access. Restoration opens the selected profile and preserves each profile’s history.
- **One server time zone defines the day.** Default Europe/Helsinki, configurable with `TRAINER_TIME_ZONE`.

## Code map and working rules

- `trainer/practice.py` selects questions, schedules reviews, and prepares feedback; `progression.py` defines unlock thresholds/order; `dual_types.py` holds the GO catalog. `views.py` handles cookies, transactions, and recovery; `models.py` defines persistence; `recovery.py` generates/normalizes phrases.
- UI lives in `trainer/templates/trainer/` and `trainer/static/trainer/`. Keep phone layouts, keyboard focus, readable type labels, and form fallback working.
- Reuse existing rules and scheduling helpers. Keep edits focused and readable. Preserve existing stored questions/reviews and add migrations for schema changes.
- Preserve CSRF checks, secure production cookies, random recovery generation, and sensitive-data redaction. Treat SQLite files and `.env` as private runtime data.
- When modifying frontend assets, update their version query in `base.html` (currently v4) so browsers fetch the new code. Form input `name="action"` shadows `form.action`; the fetch handler deliberately uses `getAttribute("action")`.
- Run relevant existing checks. Add focused regression coverage for behavior fixes, especially scheduling, repeat submissions, and recovery. UI changes also need browser verification at phone width when available.

## Run and test

From the repo root, in a development shell without production environment variables:

```powershell
# Windows setup
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

On Linux, create the venv with `python3 -m venv .venv` and use `.venv/bin/python` for the same commands. Development defaults use local `db.sqlite3`, DEBUG enabled, and localhost. Gunicorn installs only on non-Windows platforms.

```powershell
.\.venv\Scripts\python manage.py test
.\.venv\Scripts\python manage.py makemigrations --check --dry-run
git diff --check
```

Production instructions and templates are in README.md and `deploy/`. Settings read process environment; Django does not automatically load `.env`. systemd reads `/srv/typecamp/.env`, migrates before startup, and owns `/var/lib/typecamp/db.sqlite3`. Nginx serves collected static files and proxies to Gunicorn on 127.0.0.1:8100 with HTTPS configured by Certbot. Preserve the secret key and database during updates.

## Known issues and next work

These are follow-up candidates; select work according to the current user request.

- **Concurrent device UX.** Devices share one active question. An outdated question token silently returns the latest state, discarding that submission. Add explicit feedback and test overlapping requests.
- **Recovery limits.** Restore attempts have no rate limiting. Rotating a phrase cannot revoke existing device cookies. Consider throttling and a deliberate device-revocation design if requested.
- **Learning introduction.** New players enter a quiz immediately; the teaching note and unlock explanation are optional. A brief introduction remains a follow-up candidate.
- **Verification gaps.** Ubuntu deployment and physical-phone layout have not been verified in this workspace. Browser QA uses responsive viewport overrides and an isolated preview database.

Verified 2026-11-25 on Windows/Python 3.14.3: 15 Django tests pass; system checks and migration drift checks pass. Coverage includes unlock boundaries/completion, allowed moves and defenders, first/final dual feedback, skip modes, migration/history preservation, GO examples, unlimited practice, duplicate answers, spacing, day rollover, and recovery across two clients. Browser QA at 390px and 320px verified answer feedback, first single/dual unlocks, continuation, both skip modes, saved progress, and readable layouts without horizontal overflow. Simultaneous browser requests remain untested.
