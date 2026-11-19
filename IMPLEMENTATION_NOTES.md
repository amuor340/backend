# Pseudosphere Academy Django update notes

## Changes in this update
- Registration passes request context to the serializer and scopes staff profiles to the School Admin's school.
- School Admin registration is restricted to Teacher, Parent, Student, Accountant and Academic Coordinator roles.
- The platform Super Admin registration endpoint is restricted to creating School Admin accounts.
- Fee account queries use the classroom's school as the canonical school boundary, including for legacy student rows whose `school` field is blank.
- Fee payment totals are recalculated after every payment save and deletion, based only on successful payments.
- Academic Coordinators no longer receive the fee endpoints reserved for school/platform finance roles.

## Before production
- Configure a real SMTP email backend and `FRONTEND_URL` for password reset.
- Configure production secrets, allowed hosts, CORS, HTTPS, database backups and M-Pesa credentials.
- Test role permissions and school isolation with separate accounts for each role.
