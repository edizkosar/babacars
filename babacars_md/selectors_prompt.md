# Prompt: Implement All Selectors

## Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- selectors.md
- accounts_models.md
- listings_models.md
- offers_models.md
- bookings_models.md
- messaging_models.md
- notifications_models.md

## Task
Implement all selector files exactly as defined in selectors.md.
One file per app. No deviations.

## Files to Create
- accounts/selectors.py
- listings/selectors.py
- offers/selectors.py
- bookings/selectors.py
- messaging/selectors.py
- notifications/selectors.py
- dashboard/selectors.py

## Rules
1. Copy code blocks from selectors.md exactly as written.
2. Add missing imports at the top of each file if not already present.
3. Add `from django.db.models import QuerySet` import to every file.
4. Do NOT add any logic, filtering, or business rules.
5. Do NOT modify function signatures.
6. Do NOT add extra functions.
7. Every function uses keyword-only arguments (*).
8. If a model does not exist yet, do not create it — raise an ImportError comment instead.

## Output
One code block per file. No explanations. No comments outside the code.
