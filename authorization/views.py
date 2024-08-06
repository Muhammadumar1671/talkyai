from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import UserSerializer
from .models import User
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
import logging
from django.shortcuts import render

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['POST'])
def signup(request):
    # Check if the email already exists
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    print(email)
    print(username)
    print(password)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists. Please use a different email.'}, status=status.HTTP_400_BAD_REQUEST)

    # Proceed with the rest of the signup process
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active = False  # Deactivate account until email is confirmed
        user.save()

        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        # Construct the activation link
        activation_link = f'http://{current_site.domain}/activate/{uid}/{token}/'

        # Log the activation link for debugging
        logger.info(f'Activation link: {activation_link}')

        mail_subject = 'Activate your account'
        message = f'Hi {user.username},\n\nPlease click on the link below to activate your account:\n{activation_link}\n\nThank you!'
        to_email = user.email

        # Send the email
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])

        return Response({'message': 'User created successfully. Please check your email to verify your account.'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
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
        return Response({'message': 'Thank you for your email confirmation. Now you can login your account.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.is_email_verified:
            token = get_token(request)  # Generate CSRF token
            #delete alll users
            User.objects.all().delete()
            return Response({'message': 'Login successful', 'csrf_token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email not verified'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def login_signup(request):
     return render(request, 'auth/login-signup.html')