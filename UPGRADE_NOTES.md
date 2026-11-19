# Upgrade notes

## Must do before deploying
1. `pip install -r requirements.txt` (django-rest-passwordreset was removed).
2. Set `SECRET_KEY` in the environment — it is now **required** when `DEBUG=False`.
3. Set `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` (Gmail: use an App Password). Without
   `EMAIL_HOST_USER` emails print to the server console, which is why reset codes never arrived.
   Test with `python manage.py send_test_email you@example.com`.
4. `python manage.py makemigrations --check` then `python manage.py migrate`.
   New migrations: accounts 0007, schools 0003, classes 0006, results 0013.

## Behaviour changes
- Password reset is code based: POST `accounts/password/reset/` {email}, then
  `accounts/password/reset/confirm/` {email, code, password}.
- JWT access token lifetime is now configurable (default 120 minutes, refresh 30 days).
- Schools choose curricula (`education_systems`): Kenya CBC, Kenya High School,
  South Sudan Primary (P1–P8), South Sudan Secondary (S1–S4). Grading follows the class level.
  South Sudan grade bands are editable defaults — confirm them with your ministry's guidance.
- Student photo is mandatory at registration; other roles may add one later.
- Report cards show the school's name/logo in the header; "Pseudosphere" appears only in the footer.
  Report cards are now access-controlled (parent of the child, the student, or staff of the same school).
