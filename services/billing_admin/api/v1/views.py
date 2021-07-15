from django.http import JsonResponse


def debug(request):
    return JsonResponse(request.scope)
