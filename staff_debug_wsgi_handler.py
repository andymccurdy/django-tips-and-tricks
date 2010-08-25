from django.core.handlers import wsgi

class StaffDebugWSGIHandler(wsgi.WSGIHandler):
    "WSGI Handler that shows the debug error page if the logged in user is staff"

    def handle_uncaught_exception(self, request, resolver, exc_info):
        "Return a debug page response if the logged in user is staff"
        from django.conf import settings

        if not settings.DEBUG and hasattr(request, 'user') and request.user.is_staff:
            from django.views import debug
            return debug.technical_500_response(request, *exc_info)

        # not logged in or not a staff user, display normal public 500
        return super(StaffDebugWSGIHandler, self).handle_uncaught_exception(
            request, resolver, exc_info
            )
