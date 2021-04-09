from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadTeacherDataForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required


class UserLogin(LoginView):
    template_name = 'oeffcs/loginpage.html'


class UserLogout(LogoutView):
    template_name = 'app/logoutpage.html'


def index(request):
    user = request.user
    return render(request, 'oeffcs/index.html', {'user': user})


def UploadTeacherDataView(request):
    if (request.method == 'POST'):
        form = UploadTeacherDataForm(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            excel_file = request.FILES['excel_file']
            fs = FileSystemStorage()
            filename = fs.save(excel_file.name, excel_file)
            uploaded_file_url = fs.url(filename)
            return HttpResponse(f"{type(request.FILES['excel_file'])}")
    else:
        form = UploadTeacherDataForm()
        context = {
            'form': form,
        }
    return render(request, 'oeffcs/UploadExcel.html', context=context)
