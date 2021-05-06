from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    data_file = models.FileField(upload_to='exceldata')  # to be changed
    # reg_no = models.CharField(max_length=9, validators=[RegexValidator('^[A-Z0-9]*$',
    #                                                                    'Only valid register numbers are allowed')])
    status_value = models.IntegerField(default=0)
    saveteachers = models.TextField()
    def __str__(self):
        return f'{self.user.username} Profile'
