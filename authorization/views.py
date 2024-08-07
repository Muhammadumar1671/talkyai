from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import UserSerializer
from .models import User
from rest_framework.permissions import AllowAny
from .tokens import account_activation_token
from django.contrib.auth import get_user_model, authenticate, logout
from django.middleware.csrf import get_token
import logging
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import ensure_csrf_cookie


User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(email, username, password)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists. Please use a different email.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = False
        user.save()

        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        activation_link = f'http://{current_site.domain}/activate/{uid}/{token}/'
        logger.info(f'Activation link: {activation_link}')

        mail_subject = 'Activate your account'
        message = f'Hi {user.username},\n\nPlease click on the link below to activate your account:\n{activation_link}\n\nThank you!'
        to_email = user.email

        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])

        return Response({'message': 'User created successfully. Please check your email to verify your account.'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_email_verified = True
        user.is_active = True
        user.save()
        return Response({'message': 'Thank you for your email confirmation. Now you can log in to your account.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        if user.is_email_verified:
            auth_login(request, user)  # This logs the user in and creates a session
            csrf_token = get_token(request)  # Get the CSRF token for the current session
            return Response({'message': 'Login successful', 'csrf_token': csrf_token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email not verified'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([AllowAny])
def login_signup(request):
    return render(request, 'auth/login-signup.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
