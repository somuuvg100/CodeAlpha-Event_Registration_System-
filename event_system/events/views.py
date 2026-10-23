from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "ok"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_endpoint(request):
    return JsonResponse({
        "message": "This is a protected endpoint",
        "user": request.user.username
    })
