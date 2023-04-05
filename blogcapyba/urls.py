from django.urls import path
from .views import PostListView
from . import views

urlpatterns = [
    path('posts', PostListView.as_view()),
]