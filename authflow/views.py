from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from .models import CustomUser
from .serializers import (
    RegisterSerializer, LoginSerializer, OTPVerificationSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)
import random

otp_storage = {}  # Temporary in-memory storage for OTPs

class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = str(random.randint(100000, 999999))
            otp_storage[user.email] = {'otp': otp, 'expires_at': now() + timedelta(minutes=3)}
            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp}',
                'noreply@example.com',
                [user.email]
            )
            return Response({'message': 'User registered. OTP sent to email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerificationView(APIView):
    @swagger_auto_schema(request_body=OTPVerificationSerializer)
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            if email in otp_storage:
                if otp_storage[email]['otp'] == otp:
                    if otp_storage[email]['expires_at'] > now():
                        user = CustomUser.objects.filter(email=email).first()
                        if user:
                            user.is_active = True
                            user.save()
                            del otp_storage[email]
                            return Response({'message': 'OTP verified. User activated.'}, status=status.HTTP_200_OK)
                        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
                    del otp_storage[email]  # Remove expired OTP
                    return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'OTP not found for this email.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = CustomUser.objects.filter(email=email).first()
            if user and user.check_password(password):
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'token': token.key}, status=status.HTTP_200_OK)
                otp = str(random.randint(100000, 999999))
                otp_storage[email] = {'otp': otp, 'expires_at': now() + timedelta(minutes=3)}
                send_mail(
                    'Your OTP Code',
                    f'Your OTP is {otp}',
                    'noreply@example.com',
                    [email]
                )
                return Response({'error': 'User not active. OTP sent to email.'}, status=status.HTTP_403_FORBIDDEN)
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                otp = str(random.randint(100000, 999999))
                otp_storage[email] = {'otp': otp, 'expires_at': now() + timedelta(minutes=3)}
                send_mail(
                    'Your OTP Code for Password Reset',
                    f'Your OTP is {otp}. It will expire in 3 minutes.',
                    'noreply@example.com',
                    [email]
                )
                return Response({'message': 'OTP sent to email for password reset.'}, status=status.HTTP_200_OK)
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            otp = serializer.validated_data.get('otp')  # Get OTP from the request

            if email in otp_storage:
                if otp_storage[email]['otp'] == otp:
                    if otp_storage[email]['expires_at'] > now():
                        user = CustomUser.objects.filter(email=email).first()
                        if user:
                            user.set_password(new_password)
                            user.save()
                            del otp_storage[email]  # Remove OTP after successful reset
                            return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
                        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
                    del otp_storage[email]  # Remove expired OTP
                    return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'OTP not found for this email.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)