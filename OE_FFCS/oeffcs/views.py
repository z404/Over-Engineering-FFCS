from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadFileForm, ChangeStatusForm, ChangeTeachersForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .backend import convertToForm
import json

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

        # For Each status, a variable needs to be made
        st0 = True if status >= 0 else False
        st1 = True if status > 0 else False
        st2 = True if status > 1 else False
        st3 = True if status > 2 else False
        # Add rest later

        context = {'st0': st0, 'st1': st1, 'st2': st2, 'st3': st3, 'user': user}
    else:
        context = {'st0': False, 'st1': False, 'st2': False, 'st3': False, 'user': user}
    return render(request, 'oeffcs/index.html', context)


@login_required
def upload_file(request):
    if request.method == 'POST':
        # try:
        print(request.POST)
        form = UploadFileForm(request.POST, request.FILES,
                              instance=request.user.profile)
        if form.is_valid():
            form.save()
        form = ChangeStatusForm({'status_value': 1},
                                instance=request.user.profile)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
        return HttpResponseRedirect('/')
        # except User.profile.RelatedObjectDoesNotExist:
        #     form = UploadFileForm(request.POST, request.FILES)
        #     if form.is_valid():
        #         # file is saved
        #         form.instance.user = request.userz
        #         form.save()
        #         return HttpResponseRedirect('/oeffcs')
    else:
        form = UploadFileForm()
    return render(request, 'oeffcs/uploadexcel.html', {'form': form})


@login_required
def pickteachers(request):
    teacherdata = str(request.user.profile.data_file)
    ret = convertToForm(teacherdata)
    if request.method == 'POST':
        postdata = dict(request.POST)
        del postdata['csrfmiddlewaretoken']
        print(postdata)
        if postdata == {}:
            return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': 'Please choose a subject'})
        else:
            for course, teachers in postdata.items():
                if course not in teachers:
                    return render(request, 'oeffcs/pickteachers.html', \
                        {'teacherdata': ret, 'errordisplay': 'How did you even get this error?'})
                elif len(teachers) == 1:
                    return render(request, 'oeffcs/pickteachers.html', \
                        {'teacherdata': ret, 'errordisplay': 'You\'ve chosen a subject with 0 teachers!'})
            form = ChangeStatusForm({'status_value': 2}, instance=request.user.profile)
            if form.is_valid():
                form.instance.user = request.user
                form.save()
            
            form = ChangeTeachersForm({'saveteachers':json.dumps(postdata)}, instance=request.user.profile)
            if form.is_valid():
                form.instance.user = request.user
                form.save()
            return HttpResponseRedirect('/')
    return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': ''})
