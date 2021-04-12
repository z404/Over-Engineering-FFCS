from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadFileForm, ChangeStatusForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


class UserLogin(LoginView):
    template_name = 'oeffcs/loginpage.html'


class UserLogout(LogoutView):
    # template_name = 'oeffcs/logoutpage.html'
    pass

def index(request):
    user = request.user
    # try: 
    #     print(request.user.profile.reg_no)
    # except User.profile.RelatedObjectDoesNotExist:
    if request.user.is_authenticated:
        try:
            status = request.user.profile.status_value
        except User.profile.RelatedObjectDoesNotExist:
            form = ChangeStatusForm({'status_value': 0})
            if form.is_valid():
                form.instance.user = request.user
                form.save()
            status = 0
        
    return render(request, 'oeffcs/index.html', {'user': user})

@login_required
def upload_file(request):
    if request.method == 'POST':
        # try:
        print(request.POST)
        form = UploadFileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/oeffcs')
        # except User.profile.RelatedObjectDoesNotExist:
        #     form = UploadFileForm(request.POST, request.FILES)
        #     if form.is_valid():
        #         # file is saved
        #         form.instance.user = request.user
        #         form.save()
        #         return HttpResponseRedirect('/oeffcs')
    else:
        form = UploadFileForm()
    return render(request, 'oeffcs/uploadexcel.html', {'form': form})
