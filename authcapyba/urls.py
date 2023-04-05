from django.urls import path
from .views import RegisterView, LoginView, LogoutView, VerifyEmailView,PDFUploadView, UptadeUser

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('autenticate', VerifyEmailView.as_view()),
    path('pdf-url', PDFUploadView.as_view()),
    path('uptade-user', UptadeUser.as_view())
]