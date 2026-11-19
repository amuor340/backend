# Pseudosphere role separation update

- `SUPER_ADMIN` is the platform-level role and has a separate platform dashboard.
- `SCHOOL_ADMIN` operates one school and retains the existing school dashboard and school-scoped workflows.
- `GET /api/schools/platform-dashboard/` is restricted to a platform super admin and reports aggregate counts and recent school registrations.
- Platform school approvals remain restricted to platform super admins.
- Platform messaging is limited to school administrator recipients.
- `accounts.platform_boundary_authentication.PlatformBoundaryJWTAuthentication` denies platform admins access to school-operational API prefixes.

## Apply and verify

The update adds no database model fields, so it does not require a new migration. In the activated project environment, run:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

Then test logins for one platform super admin and one school admin. The super admin should land at `/platform-dashboard`; a school admin should land at `/admin-dashboard`.
