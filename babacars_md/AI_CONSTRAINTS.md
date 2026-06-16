# AI_CONSTRAINTS.md

## Purpose
This file defines absolute rules for all AI-assisted code generation in the BabaCars project.
Every rule here overrides any assumption, convention, or default behavior the AI may have.
Read this file before reading any other file. Apply these rules to every output.

---

## 1. SCOPE

- Implement ONLY what is defined in the provided MD file.
- Do NOT add features, functions, fields, or logic not explicitly specified.
- Do NOT make assumptions. If something is unclear, leave a TODO comment and do not invent a solution.
- Do NOT refactor, reorganize, or improve existing code unless explicitly instructed.

---

## 2. ARCHITECTURE

- Architecture is MTV + Service Layer. Respect layer boundaries at all times.
- `models.py` → Data definition only. No business logic. No imports from services or selectors.
- `services.py` → Business logic only. No ORM queries. No HTTP logic. Always calls selectors.py for data access.
- `selectors.py` → ORM queries only. No business logic. No HTTP logic. Returns QuerySet or model instance.
- `views.py` → HTTP logic only. No ORM queries. No business logic. Calls services and selectors only.
- `forms.py` → Validation only. No business logic. No ORM queries.
- `serializers.py` → Serialization only. No business logic.
- NEVER write ORM queries in views.py, services.py, or forms.py.
- NEVER write business logic in models.py, views.py, or selectors.py.

---

## 3. CODE STYLE

- All functions use keyword-only arguments: `def func(*, arg1, arg2):`
- All function return types must be annotated.
- All models use explicit `db_table` in Meta class.
- All models define `__str__` method.
- All choice fields use a defined CHOICES constant in the same file.
- Use `settings.AUTH_USER_MODEL` and `get_user_model()` — never import User model directly.
- No hardcoded strings for status values — always reference the CHOICES constant.
- No print statements. No commented-out code. No dead code.
- Follow PEP8. Max line length 100 characters.

---

## 4. ERROR HANDLING

- Services raise `ValueError` for business rule violations.
- Services raise `PermissionError` for authorization violations.
- Views catch `ValueError` and `PermissionError` — never let them propagate to the template.
- AJAX views return `JsonResponse({'error': str(e)}, status=400)` on error.
- Standard views use `django.contrib.messages` and redirect on error.
- Never return HTTP 500 for expected business errors.

---

## 5. SECURITY

- Every view that modifies data must use `@require_http_methods(["POST"])`.
- Every view that requires authentication must use `@login_required`.
- Never use `@csrf_exempt`. CSRF protection must always be active.
- Never expose raw exception messages to the user in templates.
- Never trust user input — always validate through forms.py before passing to services.

---

## 6. AJAX

- AJAX views always return `JsonResponse`.
- AJAX POST requests must include CSRF token in headers.
- AJAX responses follow this structure on success: `{'message': str, ...data}`
- AJAX responses follow this structure on error: `{'error': str}`
- Never mix AJAX and standard form submission in the same view.

---

## 7. DATABASE

- Database is SQLite. Do not use PostgreSQL-specific features.
- Always define `on_delete` behavior on every ForeignKey and OneToOneField.
- Always use `select_related` and `prefetch_related` where defined in selectors.md.
- Never use `__dict__` or `values()` to pass model data to templates — pass model instances.

---

## 8. FRONTEND

- CSS framework: Tailwind CSS utility classes only.
- Animation library: GSAP only.
- No inline styles unless absolutely unavoidable.
- No jQuery. Vanilla JS or GSAP only.
- All templates extend `base.html`.
- All templates are in `templates/<app_name>/<template_name>.html`.
- Mobile-first responsive design on every template.

---

## 9. NOTIFICATIONS

- Notifications are created ONLY via `notifications.services.create_notification()`.
- Never instantiate `Notification` model directly outside of `notifications/services.py`.
- Every service that triggers a notification must import from `notifications.services`.

---

## 10. WHAT AI MUST NEVER DO

- Never create a model not defined in the MD files.
- Never add a URL pattern not defined in the urls.py MD files.
- Never write raw SQL.
- Never use `eval()` or `exec()`.
- Never store sensitive data (passwords, tokens) in models beyond Django's built-in auth.
- Never add `__all__` exports unless explicitly requested.
- Never auto-generate migrations — migrations are run manually by the developer.
- Never modify `settings.py` beyond what is explicitly defined in PROJECT_OVERVIEW.md.
- Never add third-party packages not listed in the project stack.
- Never make decisions on behalf of the developer — add a TODO comment instead.

---

## 11. HEALTHCHECK PROTOCOL

After writing every file, AI must:

1. Run the healthcheck commands defined at the bottom of the relevant MD file.
2. Report the output in this exact format:

```
HEALTHCHECK REPORT — <filename>
--------------------------------
python manage.py check     → OK / ERRORS (list errors)
python manage.py test      → OK / FAILURES (list failures)
Manual verifications       → PASS / FAIL (list failures)
--------------------------------
STATUS: PASS ✅ / FAIL ❌
```

3. If STATUS is FAIL → fix all errors before moving to the next file.
4. Never proceed to the next file if healthcheck fails.
5. Never report PASS if the commands were not actually run.
