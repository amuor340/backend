from .models import AuditEvent

class ApiAuditMiddleware:
    """Record API write activity without storing request bodies or secrets.

    DRF JWT authentication runs after Django middleware, so this middleware attempts
    to resolve a valid bearer token for actor attribution when session auth is absent.
    """
    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/") and request.method in self.WRITE_METHODS and not request.path.startswith("/api/schema"):
            user = getattr(request, "user", None)
            if not user or not getattr(user, "is_authenticated", False):
                try:
                    from rest_framework.request import Request
                    from rest_framework_simplejwt.authentication import JWTAuthentication
                    result = JWTAuthentication().authenticate(Request(request))
                    user = result[0] if result else None
                except Exception:
                    user = None
            try:
                authenticated = bool(user and getattr(user, "is_authenticated", False))
                AuditEvent.objects.create(
                    school_id=getattr(user, "school_id", None) if authenticated else None,
                    actor=user if authenticated else None, method=request.method,
                    path=request.path[:500], status_code=response.status_code,
                    ip_address=self._ip(request),
                )
            except Exception:
                pass
        return response
    @staticmethod
    def _ip(request):
        value = request.META.get("REMOTE_ADDR")
        return value or None
