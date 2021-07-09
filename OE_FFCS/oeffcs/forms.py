from django.forms import ModelForm, FileInput
from oeffcs.models import Profile


class UploadFileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['data_file']
        widgets = {'data_file': FileInput(attrs={'class': 'filestyle'}),}

class ChangeStatusForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['status_value']

class ChangeTeachersForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['saveteachers']

class ChangeFiltersForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['savefilters']

class ChangeTimetableNumber(ModelForm):
    class Meta:
        model = Profile
        fields = ['timetable_count']

class ChangeOrderOfTeacher(ModelForm):
    class Meta:
        model = Profile
        fields = ['save_order']

class ChangeStatusOfShare(ModelForm):
    class Meta:
        model = Profile
        fields = ['shared_timetable']
    
class ChangeCourseType(ModelForm):
    class Meta:
        model = Profile
        fields = ['course_type']