from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadFileForm
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


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES,
                              instance=request.user.profile)
        if form.is_valid():
            # file is saved
            form.save()
            return HttpResponseRedirect('/oeffcs')
    else:
        form = UploadFileForm()
    return render(request, 'oeffcs/uploadexcel.html', {'form': form})
