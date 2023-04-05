
from django.contrib import admin
from django.urls import path, include
from blogcapyba import urls as blog_urls
from authcapyba import urls as auth_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('blogcapyba/', include(blog_urls)),
    path('auth/', include(auth_urls))
]
