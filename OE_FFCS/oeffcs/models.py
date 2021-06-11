from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.base import Model

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    data_file = models.FileField(upload_to='exceldata')  # to be changed
    # reg_no = models.CharField(max_length=9, validators=[RegexValidator('^[A-Z0-9]*$',
    #                                                                    'Only valid register numbers are allowed')])
    status_value = models.IntegerField(default=0)
    saveteachers = models.TextField()
    savefilters = models.TextField()
    timetable_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.user.username}\'s Profile'

class Timetable(models.Model):
    level = models.ForeignKey(Profile, on_delete=models.CASCADE)
    total8classes = models.IntegerField(default=0)
    total2classes = models.IntegerField(default=0)
    total6classes = models.IntegerField(default=0)
    lab_status = models.CharField(max_length=10)
    theory_status = models.CharField(max_length=10)
    ttid = models.CharField(max_length=75)
    nickname = models.CharField(max_length=75)
    priority = models.IntegerField(default=2)
    
    def __str__(self):
        return str(self.pk)

class Entry(models.Model):
    level=models.ForeignKey(Timetable, on_delete=models.CASCADE)
    slots=models.CharField(max_length=20)
    class_code=models.CharField(max_length=50)
    course_code=models.CharField(max_length=10)