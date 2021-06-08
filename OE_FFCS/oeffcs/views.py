from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import UploadFileForm, ChangeStatusForm, ChangeTeachersForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .backend import convertToForm, show_selected_data, timetable_to_html_str, generate_time_tables, query_database
import json
import threading


class UserLogin(LoginView):
    template_name = 'oeffcs/loginpage.html'


class UserLogout(LogoutView):
    # template_name = 'oeffcs/logoutpage.html'
    pass


def index(request):
    # try:
    #     print(request.user.profile.reg_no)
    # except User.profile.RelatedObjectDoesNotExist:
    # timetable_to_html_str(('L31+L32 KARPAGAM S', 'B2+TB2 PADALA KISHOR', 'L35+L36+L39+L40+L59+L60 SRIVANI A', 'L19+L20 SHARMILA BANU K',
                        #   'A1+TA1 PREETHA EVANGELINE D', 'C1+TC1+TCC1+V2 DEEPA G', 'L15+L16 GOWSALYA M', 'G1+TG1 GOWSALYA M'))
    if request.user.is_authenticated:
        try:
            status = request.user.profile.status_value
        except User.profile.RelatedObjectDoesNotExist:
            form = ChangeStatusForm({'status_value': 0})
            if form.is_valid():
                form.instance.user = request.user
                form.save()
            status = 0
        # Add rest later
    return render(request, 'oeffcs/index.html')


@login_required
def upload_file(request):
    if request.method == 'POST':
        # try:
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
        if postdata == {}:
            return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': 'Please choose a subject'})
        else:
            postdata_cleaned = {}
            for course, teachers in postdata.items():
                if course not in teachers:
                    # return render(request, 'oeffcs/pickteachers.html',
                    #               {'teacherdata': ret, 'errordisplay': 'How did you even get this error?'})
                    continue
                elif len(teachers) == 1:
                    return render(request, 'oeffcs/pickteachers.html',
                                  {'teacherdata': ret, 'errordisplay': 'You\'ve chosen a subject with 0 teachers!'})
                else:
                    postdata_cleaned.update({course:teachers})
            
            if postdata_cleaned == {}:
                return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': 'Please choose a subject'})
            # form = ChangeStatusForm(
            #     {'status_value': 2}, instance=request.user.profile)
            # if form.is_valid():
            #     form.instance.user = request.user
            #     form.save()

            form = ChangeTeachersForm(
                {'saveteachers': json.dumps(postdata)}, instance=request.user.profile)
            if form.is_valid():
                form.instance.user = request.user
                form.save()
            
            # Generating Time tables
            threadsplit = threading.Thread(target = generate_time_tables, args = (request.user,))
            threadsplit.start()
            return HttpResponseRedirect('/')
    return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': ''})


@login_required
def pickfilters(request):
    teacherdata = json.loads(request.user.profile.saveteachers)
    return render(request, 'oeffcs/pickfilters.html', {'display': teacherdata})

@login_required
def pre_check(request):
    data=dict(eval(request.body))
    return_data = query_database(data, request.user)
    return JsonResponse(data={"ret":return_data})

@login_required
def viewdata(request):
    ret = show_selected_data(request.user.profile)
    return render(request, 'oeffcs/ViewData.html', context = ret)

@login_required
def save_filters(request):
    print(dict(request.POST))
    return HttpResponseRedirect('/')