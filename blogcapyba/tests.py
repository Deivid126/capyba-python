from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from authcapyba.models import User
from .models import Post
from .serializers import PostSerializer

class PostListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
        name='test',
        email='test@example.com',
        password='testpassword',
        imagem_perfil=None
        )
        self.client.force_authenticate(user=self.user)
        self.post1 = Post.objects.create(
            title='Test Post 1', content='Test Content 1', author=self.user)
        self.post2 = Post.objects.create(
            title='Test Post 2', content='Test Content 2', author=self.user)
        self.post3 = Post.objects.create(
            title='Another Test Post', content='Test Content 3', author=self.user)

    def test_get_all_posts(self):
        url = reverse('post-list')
        response = self.client.get(url)
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_posts_with_search_query(self):
        url = reverse('post-list') + '?search=test'
        response = self.client.get(url)
        posts = Post.objects.filter(title__icontains='test') | \
            Post.objects.filter(content__icontains='test')
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_posts_with_pagination(self):
        url = reverse('post-list') + '?page=2&page_size=1'
        response = self.client.get(url)
        posts = Post.objects.all()[1:2]
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_posts_with_sort_field(self):
        url = reverse('post-list') + '?sort_field=title'
        response = self.client.get(url)
        posts = Post.objects.all().order_by('title')
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][2], serializer.data)

    def test_get_posts_with_is_published_field(self):
        self.post1.is_published = True
        self.post1.save()
        url = reverse('post-list') + '?is_published=True'
        response = self.client.get(url)
        posts = Post.objects.filter(is_published=True)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)
