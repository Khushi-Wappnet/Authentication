from django.urls import path
from .views import (
    RegisterView, OTPVerificationView, LoginView,
    ForgotPasswordView, ResetPasswordView, RoleView, 
    PermissionView, UserManagementView,RolePermissionListView, 
    RolePermissionDeleteView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Authentication API",
        default_version='v1',
        description="API documentation for authentication flow",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('roles/', RoleView.as_view(), name='roles'),
    path('permissions/', PermissionView.as_view(), name='permissions'),
    path('users/', UserManagementView.as_view(), name='users'),
    path('role-permissions/', RolePermissionListView.as_view(), name='role_permissions'),
    path('role-permissions/<int:pk>/', RolePermissionDeleteView.as_view(), name='delete_role_permission'),
]
