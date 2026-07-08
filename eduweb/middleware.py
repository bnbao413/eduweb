from django.shortcuts import redirect
from django.conf import settings


# URLs that unauthenticated users are allowed to visit
PUBLIC_PATHS = [
    settings.LOGIN_URL,
    '/accounts/register/',
    '/accounts/password_reset/',
    '/accounts/password_reset/done/',
    '/accounts/reset/',
    '/admin/',
]


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info
            is_public = any(path.startswith(p) for p in PUBLIC_PATHS)
            if not is_public:
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        return self.get_response(request)
