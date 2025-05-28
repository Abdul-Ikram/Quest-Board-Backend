from django.db import transaction
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
# import secrets
# from datetime import timedelta
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, EmailVerification
# from .models import User, EmailVerification, PasswordReset
from django.utils.timezone import now
# from django.template.loader import render_to_string
# from django.conf import settings
# from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from django.core.validators import validate_email
# from .helpers import generate_otp, send_email
from .helpers import send_email
from .serializers import RegisterSerializer, PasswordResetConfirmSerializer


# Create your views here.

# Health Check View:
class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status_code': 200,
            'message': 'API running successfully!',
        }, status=status.HTTP_200_OK)

# User authetication views:

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    send_email(user, email_type='registration')
                return Response({
                    'status_code': 200,
                    'message': 'Registration successful. Please check your email to verify your account.',
                    'user': {
                        'email': user.email, # type: ignore
                        'username': user.username, # type: ignore
                        'is_verified': user.is_verified # type: ignore
                    }
                }, status=status.HTTP_200_OK)

            except Exception as error:
                return Response({
                    'status_code': 500,
                    'message': f'An unexpected error occurred: {str(error)}. Please try again later.',
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'status_code': 400,
            'message': 'Invalid input. Please correct the highlighted errors and try again.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    """
    API view for verifying a user's email using an OTP.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({
                'status_code': 400,
                'message': 'Both email and OTP are required to complete the verification process.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email).first()
        
        if not user:
            return Response({
                'status_code': 404,
                'message': 'No account associated with the provided email address was found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({
                'status_code': 400,
                'message': 'This email address has already been verified.'
            }, status=status.HTTP_400_BAD_REQUEST)

        email_verification = EmailVerification.objects.filter(
            user=user,
            otp=otp,
            is_used=False,
        ).first()

        if not email_verification:
            return Response({
                'status_code': 400,
                'message': 'The provided OTP is invalid or has already been used.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if email_verification.expires_at < now():
            return Response({
                'status_code': 400,
                'message': 'The OTP has expired. Please request a new OTP and try again.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Use transaction for atomicity
        with transaction.atomic():
            email_verification.is_used = True
            email_verification.save()

            user.is_verified = True
            user.save()

        return Response({
            'status_code': 200,
            'message': 'Your email has been successfully verified. Thank you for completing the verification process.'
        }, status=status.HTTP_200_OK)

class RegenerateOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                'status_code': 400,
                'message': 'The email address is required to proceed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({
                'status_code': 404,
                'message': 'No user found with the provided email address.'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                # Check if an unexpired OTP exists
                existing_verification = EmailVerification.objects.filter(
                    user=user,
                    is_used=False
                ).order_by('-expires_at').first()

                if existing_verification and existing_verification.expires_at > now():
                    return Response({
                        'status_code': 400,
                        'message': 'An active OTP already exists. Please use it.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Generate and send a new OTP
                send_email(user, email_type='otp_regeneration')

            return Response({
                'status_code': 200,
                'message': 'A new OTP has been successfully generated and sent to your email address.'
            }, status=status.HTTP_200_OK)

        except Exception as error:
            return Response({
                'status_code': 500,
                'message': f'Failed to generate and send OTP. Error: {str(error)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token), # type: ignore
    }

class LoginView(APIView):
    """
    API view for authenticating users and returning JWT tokens upon successful login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'status_code': 400,
                'message': 'Both email and password are required to proceed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({
                'status_code': 400,
                'message': 'The email address provided is not valid. Please enter a valid email address.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({
                'status_code': 404,
                'message': 'No account associated with the provided email address was found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({
                'status_code': 401,
                'message': 'The password entered is incorrect. Please try again.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_verified:
            return Response({
                'status_code': 401,
                'message': 'Your email address has not been verified. Please verify your email before attempting to log in.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            tokens = get_tokens_for_user(user)
        except Exception as e:
            return Response({
                'status_code': 500,
                'message': f'An unexpected error occurred while generating tokens: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'status_code': 200,
            'message': 'Login successful. Welcome back!',
            'refresh': tokens['refresh'],
            'access': tokens['access'],
            'data': {
                'user': {
                    'id': user.id,  # type: ignore
                    'username': user.username,
                    'is_paid': user.is_paid,
                    'full_name': user.full_name,
                    'email': user.email,
                    'image': user.image,
                    'status': user.is_active,
                    'country': user.country,
                    'state': user.state,
                    'postal_code': user.postal_code,
                    'full_address': user.address,
                    'phone_number': user.phone_number,
                    'is_verified': user.is_verified
                }
            }
        }, status=status.HTTP_200_OK)

# forgot password reset views:
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                'status_code': 400,
                'message': 'Email is required to proceed with the password reset request.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({
                'status_code': 404,
                'message': 'No account associated with the provided email address was found.'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            send_email(user, email_type='password_reset')
            return Response({
                'status_code': 200,
                'message': 'Password reset OTP has been sent to your email address. Please check your inbox.'
            }, status=status.HTTP_200_OK)

        except Exception as error:
            return Response({
                'status_code': 500,
                'message': f'Failed to send password reset email. Error: {str(error)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Deserialize the request data
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Save the updated password
                serializer.save()
                return Response({
                    "status_code": 200,
                    "message": "Password updated successfully."
                }, status=status.HTTP_200_OK)
            except serializers.ValidationError as error: # type: ignore
                # Handle specific validation errors
                return Response({
                    "status_code": 400,
                    "message": str(error)
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                # Handle any unexpected errors
                return Response({
                    "status_code": 500,
                    "message": f"An error occurred: {str(error)}."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If the serializer is invalid, return errors
        return Response({
            "status_code": 400,
            "message": "Invalid input. Please check the provided data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteAllUsersAPIView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        count = User.objects.count()
        User.objects.all().delete()

        return Response({
            "status_code": 200,
            "message": f"All {count} users deleted successfully."
        }, status=status.HTTP_200_OK)