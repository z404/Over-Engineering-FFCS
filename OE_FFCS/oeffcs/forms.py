from django.forms import ModelForm
from oeffcs.models import Profile


class UploadFileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['data_file']

class ChangeStatusForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['status_value']

class ChangeTeachersForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['saveteachers']