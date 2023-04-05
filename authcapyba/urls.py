from django.urls import path
from .views import RegisterView, LoginView, LogoutView, VerifyEmailView,PDFUploadView, UptadeUser

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('autenticate', VerifyEmailView.as_view(),name='verify'),
    path('pdf-url', PDFUploadView.as_view(),name='pdf'),
    path('uptade-user', UptadeUser.as_view(),name='uptade')
]