from django.shortcuts import redirect
from django.conf import settings


class LoginRequiredMiddleware:
    """
    Redirect unauthenticated users to the login page for all timetable URLs.
    Exempt paths can be configured via settings.LOGIN_EXEMPT_URLS (exact or prefix match).
    Short paths like '/' and '/timetable/' are matched exactly to avoid
    accidentally exempting everything.
    """

    # Paths too short for prefix matching — use exact match instead
    EXACT_MATCH_PATHS = {'/', '/timetable/', '/timetable/home/'}

    def __init__(self, get_response):
        self.get_response = get_response

        # Default exempt prefixes — admin, static files, Django auth URLs
        self.exempt_prefixes = (
            '/admin/',
            '/accounts/login/',
            '/accounts/logout/',
        )

        # Extra URLs from settings (split into exact vs prefix)
        extra = getattr(settings, 'LOGIN_EXEMPT_URLS', [])
        self.exempt_exact = set(self.EXACT_MATCH_PATHS)
        extra_prefixes = []
        for url in extra:
            if url in self.EXACT_MATCH_PATHS:
                self.exempt_exact.add(url)
            else:
                extra_prefixes.append(url)
        self.exempt_prefixes = self.exempt_prefixes + tuple(extra_prefixes)

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info
            # Check exact matches first, then prefix matches
            if path not in self.exempt_exact:
                if not any(path.startswith(prefix) for prefix in self.exempt_prefixes):
                    login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
                    return redirect(f"{login_url}?next={path}")

        return self.get_response(request)
