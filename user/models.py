from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import User
import random, string

class CustomerUser(User):
    token = models.CharField(max_length=30, null=True, blank=True)

    @property
    def randomword(self, length=20):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def generate_token(self, token=None):
        token = self.randomword if not token else token
        while CustomerUser.objects.filter(token=token):
            token = self.randomword
        self.token = token
        self.save()

    def logout(self):
        self.token = None
        self.save()
