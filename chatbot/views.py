from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def landing_page(request):
    return render(request, 'chatbot/landingpage.html')
