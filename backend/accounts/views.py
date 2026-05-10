from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import SignupSerializer, UserProfileSerializer

User = get_user_model()


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        form = SignupSerializer(data=request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        new_user = form.save()
        tokens = RefreshToken.for_user(new_user)

        return Response({
            'user': UserProfileSerializer(new_user).data,
            'access': str(tokens.access_token),
            'refresh': str(tokens),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        pwd = request.data.get('password', '')

        if not email or not pwd:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        found_user = authenticate(request, username=email, password=pwd)

        if found_user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = RefreshToken.for_user(found_user)

        return Response({
            'user': UserProfileSerializer(found_user).data,
            'access': str(tokens.access_token),
            'refresh': str(tokens),
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        form = UserProfileSerializer(request.user, data=request.data, partial=True)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        form.save()
        return Response(form.data)
