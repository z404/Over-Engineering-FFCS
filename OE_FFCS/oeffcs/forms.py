from django.forms import ModelForm
from oeffcs.models import Profile


class UploadFileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['data_file', 'reg_no']
