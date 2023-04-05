from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO


class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    username = None
    imagem_perfil = models.ImageField(upload_to='images/', default=None)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','password']

    def save(self, *args, **kwargs):
      
        if self.imagem_perfil:
            try:
                this = User.objects.get(id=self.id)
                if this.imagem_perfil != self.imagem_perfil:
                    this.imagem_perfil.delete(save=False)
            except User.DoesNotExist:
                pass

            img_io = BytesIO()
            self.imagem_perfil.save(self.imagem_perfil.name, InMemoryUploadedFile(
                self.imagem_perfil.file,
                None,
                self.imagem_perfil.name,
                self.imagem_perfil.content_type,
                self.imagem_perfil.size,
                None,
                )
            )
        super().save(*args, **kwargs)
class PDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='pdfs/')