

## Update notes (2026-10-25)

- Added a profile-picture upload control to the shared dashboard navigation. Users can choose an image from their computer; uploads are limited to 5 MB.
- Added a school-admin student photo picker on Edit Student. When the student has a linked login account, the image is also saved to the account avatar.
- Added a full attachment URL to homework API responses and visible open/download links on parent and student homework pages.
- Added school name to the user API payload, used it for school dashboard branding, and corrected the teacher directory permission/school scoping so School Admin can see their school's teachers.
- Added a shared Pseudosphere footer to dashboard layouts and standalone homework/messages/school-admin screens.
- Added student, class, academic-year, and date filters to Fee Records.
- Removed the extra Delete Class button from the Academic Coordinator class details page and added a Back to inbox action after sending messages.
- Added a baseline color treatment for buttons without an explicit background class.

Validation: Python files pass `compileall`; frontend JS/JSX passes TypeScript syntax parsing. A full Django check and Vite production build could not be run in this packaging environment because Django and the frontend dependencies are not installed here.
