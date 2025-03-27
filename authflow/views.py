from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework import status
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema
from .models import CustomUser, Role, Permission,RolePermission
from .serializers import (
    RegisterSerializer, LoginSerializer, OTPVerificationSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,RoleSerializer,
    PermissionSerializer, UserManagementSerializer,RolePermissionSerializer
)
import random
from drf_yasg import openapi

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
    
class RoleView(APIView):
    @swagger_auto_schema(responses={200: RoleSerializer(many=True)})
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=RoleSerializer, responses={201: RoleSerializer})
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PermissionView(APIView):
    @swagger_auto_schema(responses={200: PermissionSerializer(many=True)})
    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PermissionSerializer, responses={201: PermissionSerializer})
    def post(self, request):
        serializer = PermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserManagementView(APIView):
    @swagger_auto_schema(responses={200: UserManagementSerializer(many=True)})
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserManagementSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=UserManagementSerializer, responses={201: UserManagementSerializer})
    def post(self, request):
        serializer = UserManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user'),
                'role': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the role'),
            },
            required=['id', 'role']
        ),
        responses={200: UserManagementSerializer}
    )
    def patch(self, request):
        user_id = request.data.get('id')  # Get the user ID from the request
        role_id = request.data.get('role')  # Get the role ID from the request

        if not user_id or not role_id:
            return Response({'error': 'User ID and Role ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)  # Fetch the user by ID
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            role = Role.objects.get(id=role_id)  # Fetch the role by ID
        except Role.DoesNotExist:
            return Response({'error': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Update the user's role
        user.role = role
        user.save()

        serializer = UserManagementSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RolePermissionListView(ListCreateAPIView):
    """
    View to list and assign permissions to a role.
    """
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer

    def get_queryset(self):
        role_id = self.request.query_params.get('role')
        if role_id:
            return RolePermission.objects.filter(role_id=role_id)
        return super().get_queryset()

class RolePermissionDeleteView(DestroyAPIView):
    """
    View to remove a permission from a role.
    """
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer