from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, unique=True)
    mobile = models.CharField(max_length=15, null=False, validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="Only digits allowed."
            )
        ]
    )

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.username

        