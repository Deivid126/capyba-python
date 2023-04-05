
from rest_framework_simplejwt.tokens import Token, RefreshToken
from datetime import timedelta, datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import PDF
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User



class RegisterViewTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.user_data = {
            'name':'test',
            'email': 'test@example.com',
            'password': 'testpassword123',
             
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_register_user_sends_confirmation_email(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.first()
        refresh = RefreshToken.for_user(user)
        tokens = {"access": str(refresh.access_token), "refresh": str(refresh)}
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)

class LoginViewTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('login')
        self.email = 'test@example.com'
        self.password = 'testpassword'
        self.user = User.objects.create(
        name='test',
        email='test@example.com',
        password='testpassword',
        imagem_perfil=None
    )

    def test_login_success(self):
        data = {'email': self.email, 'password': self.password}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_fail_wrong_password(self):
        data = {'email': self.email, 'password': 'wrongpassword'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Incorrect password!', response.data['error'])
    
    def test_login_fail_user_not_found(self):
        data = {'email': 'notfound@example.com', 'password': 'testpassword'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User not found!', response.data['error'])

class LogoutViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
        name='test',
        email='test@example.com',
        password='testpassword',
        imagem_perfil=None
    )

        url = reverse('login')
        data = {'email': 'test@example.com', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.token = response.data['access']
        print(response.data)
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def test_logout_with_valid_token(self):
       
        url = reverse('logout')
        response = self.client.post(url, headers=self.headers)

        self.assertEqual(response.status_code, 204)
        self.assertTrue(RefreshToken(self.token).blacklisted)

    def test_logout_with_invalid_token(self):
        headers = {'Authorization': 'Bearer invalid_token'}
        url = reverse('logout')
        response = self.client.post(url, headers=headers)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(RefreshToken('invalid_token').blacklisted)

class VerifyEmailViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
        name='test',
        email='test@example.com',
        password='testpassword',
        imagem_perfil=None
    )
        self.token = RefreshToken.for_user(user=self.user)

    def test_valid_token(self):
        token = str(self.token.access_token)
        url = reverse('verify') + f'?token={token}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertTrue(self.token.used)

    def test_invalid_token(self):
        token = str(self.token.access_token)
        self.token.expiration_date = datetime.now() - timedelta(days=1)
        

        url = reverse('verify') + f'?token={token}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)
       

    def test_used_token(self):
        token = str(self.token.access_token)
        self.token.used = True
        

        url = reverse('verify') + f'?token={token}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

    def test_nonexistent_token(self):
        url = reverse('verify') + '?token=nonexistent-token'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

    def test_token_not_provided(self):
        url = reverse('verify')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

   
    def test_token_get_fails(self, mock_token_get):
        token = str(self.token.access_token)
        mock_token_get.side_effect = Token.DoesNotExist

        url = reverse('verify') + f'?token={token}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

    def test_user_not_found(self):
        token = str(self.token.access_token)
        self.user.delete()

        url = reverse('verify') + f'?token={token}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

class UptadeUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
        name='test',
        email='test@example.com',
        password='testpassword',
        imagem_perfil=None
    )
        self.token = RefreshToken.for_user(user=self.user)

    def test_update_user(self):
        token = str(self.token.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        data = {
            'password':'testpassword',
            'name': 'Doe',
            'email': 'test@example.com',
            'imagem_perfil':None
        }

        url = reverse('uptade')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'menssagem': 'Usuario autualizado com sucesso'})

class PDFUploadViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
        name='test',
        email='test@example.com',
        password='testpassword',
        imagem_perfil=None
    )
        self.token = RefreshToken.for_user(user=self.user)

    def test_upload_pdf(self):
        token = str(self.token.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        pdf_file = SimpleUploadedFile(
            'test.pdf',
            b'This is a test PDF file content.',
            content_type='application/pdf'
        )

        data = {
            'pdf': pdf_file
        }

        url = reverse('pdf')
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PDF.objects.count(), 1)
        self.assertEqual(response.data, {'id': 1})