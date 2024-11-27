from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health':
            return JsonResponse({'status': 'ok'}, status=200)
        return self.get_response(request)
