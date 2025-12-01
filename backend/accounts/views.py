from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import User, EmailVerificationToken, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserSerializer,
)
from django.middleware.csrf import get_token
import logging

# 로거 생성
logger = logging.getLogger(__name__)  # 'accounts.views'로 로그 남음


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    logger.info(
        f"User registration attempt for email: {request.data.get('email', 'unknown')}"
    )

    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            logger.info(f"User registered successfully: {user.email}")

            # Create email verification token
            token = EmailVerificationToken.objects.create(user=user)

            # Send verification email
            verification_url = (
                f"{settings.FRONTEND_URL}/auth/verify-email?token={token.token}"
            )
            subject = "Verify your email address"
            message = f"""
            Hi! {user.email},
        
            Please click the link below to verify your email address:
            {verification_url}
        
            This link will expire in 24 hours.
        
            If you didn't create an account, please ignore this email.
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            logger.info(f"Verification email sent to: {user.email}")

            return Response(
                {
                    "message": "Registration successful. Please check your email for verification.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(
                f"Registration failed for {request.data.get('email', 'unknown')}: {str(e)}"
            )
            return Response(
                {"error": "Registration failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        logger.warning(f"Invalid registration data: {serializer.errors}")

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email(request):
    serializer = EmailVerificationSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data["token"]

        try:
            verification_token = EmailVerificationToken.objects.get(token=token)

            if verification_token.is_used:
                return Response(
                    {"error": "Token already used."}, status=status.HTTP_400_BAD_REQUEST
                )

            if verification_token.is_expired():
                return Response(
                    {"error": "Token expired."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Verify email
            user = verification_token.user
            user.is_email_verified = True
            user.save()

            # Mark token as used
            verification_token.is_used = True
            verification_token.save()

            return Response(
                {"message": "Email verified successfully."}, status=status.HTTP_200_OK
            )

        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification(request):
    serializer = ResendVerificationSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)

            if user.is_email_verified:
                return Response(
                    {"error": "Email already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Invalidate old tokens
            EmailVerificationToken.objects.filter(user=user, is_used=False).update(
                is_used=True
            )

            # Create new token
            token = EmailVerificationToken.objects.create(user=user)

            # Send verification email
            verification_url = (
                f"{settings.FRONTEND_URL}/auth/verify-email?token={token.token}"
            )
            subject = "Verify your email address"
            message = f"""
            Hi! {user.email},
            
            Please click the link below to verify your email address:
            {verification_url}
            
            This link will expire in 24 hours.
            
            If you didn't create an account, please ignore this email.
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response(
                {"message": "Verification email sent."}, status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        login(request, user)

        return Response(
            {"message": "Login successful.", "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]

        # User exists (validated by serializer), proceed with token creation
        user = User.objects.get(email=email)

        # Invalidate old tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        # Create new token
        token = PasswordResetToken.objects.create(user=user)

        # Send password reset email
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token.token}"
        subject = "Password Reset Request"
        message = f"""
        Hi! {user.email},
    
        You requested a password reset. Please click the link below to reset your password:
        {reset_url}
    
        This link will expire in 1 hour.
    
        If you didn't request a password reset, please ignore this email.
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "Password reset email sent."}, status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            reset_token = PasswordResetToken.objects.get(token=token)

            if reset_token.is_used:
                return Response(
                    {"error": "Token already used."}, status=status.HTTP_400_BAD_REQUEST
                )

            if reset_token.is_expired():
                return Response(
                    {"error": "Token expired."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Reset password
            user = reset_token.user
            user.set_password(password)
            user.save()

            # Mark token as used
            reset_token.is_used = True
            reset_token.save()

            return Response(
                {"message": "Password reset successfully."}, status=status.HTTP_200_OK
            )

        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_csrf_token(request):
    token = get_token(request)
    return Response({"csrfToken": token})
