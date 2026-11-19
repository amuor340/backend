# Pseudosphere Academy: audit and implementation report

## Approved features implemented in this package
- Student homework submissions with one submission per student/assignment, attachment/text response, late status, and staff grading/feedback API.
- Authenticated write-request audit events (method, URL path, status, actor, school, IP; request bodies and passwords are deliberately not logged). School-scoped audit feed for authorized staff.
- Alerts API for homework deadlines within three days and same-day recorded absences, scoped to school and role.
- Timetable overlap validation rejects overlapping active periods for the same teacher or classroom in the same day, term, and academic year.
- Student CSV export endpoint and a portable JSON backup management command.
- Teacher homework route registered in React to match the existing sidebar link.
- Attendance history permission allows any teacher with an active assignment to pass the permission gate; marking remains governed by the existing class-teacher checks in attendance views.

## Important architecture findings retained for follow-up
- `accounts.StudentProfile` and `students.Student` are distinct models. They were not merged because login/profile flows and academic/attendance foreign keys may rely on different records. A data migration and explicit linking policy should precede any consolidation.
- Class teacher is represented in both `ClassRoom.class_teacher` and `TeacherAssignment.is_class_teacher`. This patch does not silently merge those sources because doing so can change existing school assignments. A one-time reconciliation report and school-approved canonical rule are still needed.
- Profile image fields already exist (`CustomUser.profile_picture` and `Student.photo`); UI/API end-to-end upload validation still needs integration testing against the actual auth/profile serializers and deployment media storage.
- The existing app is named `luma_2000_academy` internally. It was not renamed because renaming Django's project package affects deployment imports and environment configuration.

## API additions
- `GET /api/assignments/submissions/` and `POST /api/assignments/submissions/` for students; `PATCH` for eligible students/staff.
- `GET /api/school-tools/alerts/`
- `GET /api/school-tools/audit-events/`
- `GET /api/school-tools/exports/students.csv`
- Management command: `python manage.py backup_school_data --output-dir ./backups`

## Validation status
- Static Python compilation and frontend production build/lint should be run in an environment with the project's dependencies installed. This audit environment does not have Django installed, so Django system checks, migration checks, and API tests cannot be truthfully marked as passed here. The new migration is included, but must be checked against the project's actual migration graph before deployment.
- The timetable check is serializer-level and therefore applies to DRF create/update endpoints; direct ORM writes and bulk imports should call `full_clean()` or run an equivalent conflict validator.
- Backups contain sensitive school data. Store them in restricted storage and test restore procedures before relying on them for disaster recovery.

## Validation performed in the packaging environment (2026-10-25)
- `python -m compileall` over the backend source: **PASS** (all Python files compile).
- ZIP structure and archive integrity: **checked during packaging**.
- Django `check`, migration graph, and Django test suite: **NOT RUN** because Django is not installed in this execution environment.
- React production build and ESLint: **NOT RUN**. `npm ci --ignore-scripts --no-audit --no-fund` did not complete within the available execution window, so dependencies were not installed. No claim of a passing frontend build is made.
- Live API, file upload/media storage, database migration against real data, and backup restoration: **NOT RUN** because no configured application database or deployment credentials are available here.

## Deployment checklist before using these changes
1. In a clean backend environment, install `requirements.txt`, then run `python manage.py check` and `python manage.py showmigrations`.
2. Run `python manage.py migrate` against a backup or staging database first. Review the migration plan; do not apply to production until it is clean.
3. Run `python manage.py test` and add integration tests for student submission, role boundaries, alert scoping, and timetable overlaps.
4. In the frontend directory, run `npm ci`, `npm run lint`, and `npm run build`.
5. Test student account linking: the homework submission API requires `students.Student.user` to point to the student's login account.
6. Test the backup command and restore the JSON dump into a disposable database. The JSON dump is a data export, not a byte-for-byte database snapshot and does not include uploaded media files.

## Follow-up: Django duplication and consistency pass
- Added `accounts.permissions.RolePermission` as the canonical authenticated role-check primitive.
- Refactored dashboard and reports role-permission base classes, fee permissions, parent super-admin permission, student admin/coordinator permission, and the legacy `accounts.permisions` module to reuse the shared primitive.
- Kept app-specific role lists unchanged. This is important because identically named permissions in the existing code do not all grant the same roles; flattening them into one policy would silently change access.
- Kept `accounts.permisions` as a compatibility shim so existing imports continue to work. New imports should use `accounts.permissions`.
- The audit also found repeated display helper patterns (`get_student_name`, `get_classroom_name`) and separate `Term` models across apps. These are not automatically interchangeable: their model relations and term semantics need to be checked before extracting helpers or merging models.
- `accounts.StudentProfile` versus `students.Student`, and `ClassRoom.class_teacher` versus `TeacherAssignment.is_class_teacher`, remain explicit data-model consolidation tasks. They require a mapping/reconciliation migration and tests before any source is removed.
