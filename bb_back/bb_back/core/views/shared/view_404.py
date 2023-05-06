from django.http import JsonResponse
from rest_framework import status


def view_404(request, exception=None):
    return JsonResponse(
        data={
            "response_data": None,
            "success": False,
            "status_code": status.HTTP_404_NOT_FOUND,
            "message": f"No avaliable resources found on {request.path}"
        })
