from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import BasePermission
from django.db.models import Q
from rest_framework import status
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from.serializers import UserSerializer,PDFObjSerializer
from rest_framework.authtoken.models import Token
from .utils import send_confirmation_email
from .models import User, PDF
import jwt, datetime

# Create your views here.
class RegisterView(APIView):
    
    def post(self, request):

        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = User.objects.get(email=request.data.get('email'))
        
        refresh = RefreshToken.for_user(user)

        tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}
        
        send_confirmation_email(user.email,token=tokens.get('access'))

        return response(serializer.data)

    
class LoginView(APIView):

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        refresh = RefreshToken.for_user(user)

        tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}

        response = Response()

        response.data = tokens
        
        return response
class LogoutView(APIView):
    def post(self, request):
        
        try:
           
            token = request.headers['Authorization'].split()[1]
            refresh_token = RefreshToken(token)
            refresh_token.blacklist()
            return Response({'menssagem': 'Logout realizado com sucesso.'}, status=204)
        
        except:
           
            return Response({'mensagem': 'Não foi possível realizar o logout.'}, status=400)
        
class VerifyEmailView(APIView):
    def get(self, request):
        
        try:
            token_key = request.GET.get('token')
            token_obj = Token.objects.get(key=token_key)
        except (Token.DoesNotExist, TypeError):
            return Response({'menssagem':'Token não existe'})

        if token_obj.expiration_date < datetime.now() or token_obj.used:
            return Response({'menssagem':'Token expirou'})

        try:
            user = User.objects.get(email=token_obj.email)
            user.is_verified = True
            user.save()

            token_obj.used = True
            token_obj.save()
        except User.DoesNotExist:
            return Response({'menssagem':'Usuario não existe'})

        return Response({'menssagem':'Usuario autenticado'})
    
class UptadeUser(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'menssagem':'Usuario autualizado com sucesso'})

class PDFUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = PDFObjSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['pdf']
            pdf_obj = PDF.objects.create(user=request.user, pdf_file=pdf_file)
            return Response({'id': pdf_obj.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)