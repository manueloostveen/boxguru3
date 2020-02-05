from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # add additional fields in here
    email = models.EmailField(max_length=254, blank=False, null=False)

    def __str__(self):
        return self.email
