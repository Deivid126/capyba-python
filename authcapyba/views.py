
from venv import logger
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from.serializers import UserSerializer,PDFObjSerializer, LoginSerializer
from .utils import send_confirmation_email
from .models import User, PDF
from datetime import datetime
from django.conf import settings
import jwt


# Create your views here.
class RegisterView(APIView):
    @api_view(http_method_names=["POST"])
    @permission_classes([AllowAny])
    def post(self, request):

        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = User.objects.get(email=request.data.get('email'))
        
        refresh = RefreshToken.for_user(user)

        tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}
        
        try:
            send_confirmation_email(user.email, token=tokens.get('access'))
        except Exception as e:
            logger.exception('Error sending confirmation email')

       
        return Response(serializer.data)

    
class LoginView(APIView):

    @api_view(http_method_names=["POST"])
    @permission_classes([AllowAny])
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({'error': 'Incorrect password!'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}

        return Response(tokens, status=status.HTTP_200_OK)
class LogoutView(APIView):
    
    @api_view(http_method_names=["POST"])
    @permission_classes([IsAuthenticated])
    def post(self, request):
        
        try:
           
            token = request.headers['Authorization'].split()[1]
            refresh_token = RefreshToken(token)
            refresh_token.blacklist()
            return Response({'menssagem': 'Logout realizado com sucesso.'}, status=204)
        
        except:
           
            return Response({'mensagem': 'Não foi possível realizar o logout.'}, status=400)
        
class VerifyEmailView(APIView):
    @api_view(http_method_names=["GET"])
    @permission_classes([AllowAny])
    def get(self, request):
        token_key = request.GET.get('token')
        
        if not token_key:
            return Response({'menssagem': 'Token não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = jwt.decode(token_key, settings.SECRET_KEY, algorithms=['HS256'])
            email = decoded_token['email']
            expiration_time = datetime.fromtimestamp(decoded_token['exp'])
            token_obj = RefreshToken(token=token_key, user=User.objects.get(email=email))
        except (jwt.exceptions.InvalidTokenError, User.DoesNotExist, KeyError):
            return Response({'menssagem': 'Token inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.used:
            return Response({'menssagem': 'Token já utilizado.'}, status=status.HTTP_400_BAD_REQUEST)

        if expiration_time < datetime.now():
            return Response({'menssagem': 'Token expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.is_verified = True
        user.save()

        return Response({'menssagem': 'Email verificado com sucesso.'}, status=status.HTTP_200_OK)
class UptadeUser(APIView):

    @api_view(http_method_names=["POST"])
    @permission_classes([IsAuthenticated])
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'menssagem':'Usuario autualizado com sucesso'})

class PDFUploadView(APIView):
    

    @api_view(http_method_names=["POST"])
    @permission_classes([AllowAny])
    def post(self, request, format=None):
        serializer = PDFObjSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['pdf']
            pdf_obj = PDF.objects.create(user=request.user, pdf_file=pdf_file)
            return Response({'id': pdf_obj.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
