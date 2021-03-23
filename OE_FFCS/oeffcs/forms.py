from django.forms import forms


class UploadTeacherDataForm(forms.Form):
    excel_file = forms.FileField(label='Choose Excel file:\t\t')
