from django.db import models
from authcapyba.models import User



class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
