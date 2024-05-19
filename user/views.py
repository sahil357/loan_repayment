from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login, logout
from user.serializers import UserSerializer
from user.models import CustomerUser

class AuthViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], url_path='create', url_name='create')
    def create_user(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            CustomerUser.objects.create(**serializer.validated_data)
            return Response({'message': 'User Successfully Created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': 'Unable to create user - {}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login', url_name='login')
    def login(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = CustomerUser.objects.filter(username=username, password=password).last()
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        user.generate_token()
        return Response({'message': 'Logged in successfully', 'token': user.token}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='logout', url_name='logout')
    def logout(self, request):
        user = request.user
        user.logout()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

