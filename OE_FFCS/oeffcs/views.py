from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, request
from .forms import UploadFileForm, ChangeStatusForm, ChangeTeachersForm, ChangeOrderOfTeacher, ChangeStatusOfShare, ChangeCourseType
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from .backend import convertToForm, get_timetable_data_by_id, show_selected_data, generate_time_tables, query_database, savefilters, backend_genteachlist
from .backend import apicall_render_next, apicall_changepriority_by_id, apicall_changenick_by_id, apicall_timetable_boilerplate
from .backend import display_teacher_list_temp, people_status, apicall_finalpage
from .models import Timetable
import json
import threading
import os
import time


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
            if request.user.profile.status_value >= 1:
                try:
                    os.remove(settings.MEDIA_ROOT+'\\exceldata\\'+request.user.profile.data_file.name.replace(" ","_"))
                except:
                    pass
            form.save()
        form = ChangeStatusForm({'status_value': 1},
                                instance=request.user.profile)
        
        if form.is_valid():
            print("I'm here")
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
    # teacherdata = str(request.user.profile.data_file)
    ret = convertToForm(request.user)
    if request.method == 'POST':
        postdata = dict(request.POST)
        del postdata['csrfmiddlewaretoken']
        if postdata == {}:
            return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': 'Please choose a subject'})
        else:
            postdata_cleaned = {}
            course_type_save_dict = {}
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
                    try:
                        course_type_save_dict[course] = dict(request.POST)[course+'classification'][0]
                    except KeyError:
                        return render(request, 'oeffcs/pickteachers.html',
                                  {'teacherdata': ret, 'errordisplay': 'Please select your course type for all subjects!'})
            
            if postdata_cleaned == {}:
                return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': 'Please choose a subject'})
            # form = ChangeStatusForm(
            #     {'status_value': 2}, instance=request.user.profile)
            # if form.is_valid():
            #     form.instance.user = request.user
            #     form.save()
            form = ChangeCourseType({'course_type': course_type_save_dict}, instance=request.user.profile)
            if form.is_valid():
                form.instance.user = request.user
                form.save()
            form = ChangeTeachersForm(
                {'saveteachers': json.dumps(postdata_cleaned)}, instance=request.user.profile)
            if form.is_valid():
                form.instance.user = request.user
                form.save()
            
            # Generating Time tables
            form = ChangeStatusForm(
                {'status_value': 1}, instance=request.user.profile)
            if form.is_valid():
                form.instance.user = request.user
                form.save()
            threadsplit = threading.Thread(target = generate_time_tables, args = (request.user,))
            threadsplit.start()
            return HttpResponseRedirect('/timetablesgenerating/')
    return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': ''})


@login_required
def pickfilters(request):
    teacherdata = json.loads(request.user.profile.saveteachers)
    return render(request, 'oeffcs/pickfilters.html', {'display': teacherdata})

@login_required
def pre_check(request):
    data=dict(eval(request.body))
    return_data = query_database(data, request.user)
    return JsonResponse(data={"ret":len(return_data)})

@login_required
def viewdata(request):
    try:
        ret = show_selected_data(request.user.profile)
    except User.profile.RelatedObjectDoesNotExist:
        ret = {'exceldata': 'You haven\'t uploaded a file yet!',
        'teacherdata': 'You haven\'t chosen any teachers yet!',
        'filters': 'You haven\'t chosen any filters yet!', 
        'saved_teacher_list': 'You haven\'t generated a teacher list yet!'}
        form = ChangeStatusForm({'status_value': 0})
        if form.is_valid():
            form.instance.user = request.user
            form.save()

    if request.user.profile.status_value != -5:
        return render(request, 'oeffcs/ViewData.html', context = ret)
    else:
        return HttpResponseRedirect('/timetablesgenerating/')


@login_required
def save_filters(request):
    filters = dict(request.POST)
    del filters['csrfmiddlewaretoken']
    savefilters(filters, request.user)
    return HttpResponseRedirect('/')

@login_required
def tablepriority(request):
    # ret = apicall_getselectedtt(request.user)
    ret = apicall_render_next(request.user, 0, 'first')
    return render(request, 'oeffcs/TablePriority.html', ret)

@login_required
def api_render_tt(request):
    post_data = dict(eval(request.body))
    ret = apicall_render_next(request.user, post_data['index'])
    return JsonResponse(ret)

@login_required
def api_score_change(request):
    post_data = dict(eval(request.body))
    apicall_changepriority_by_id(request.user, post_data['index'], post_data['score'])
    return JsonResponse({})

@login_required
def api_nickname_change(request):
    post_data = dict(eval(request.body))
    apicall_changenick_by_id(request.user, post_data['index'], post_data['nick'])
    return JsonResponse({})

@login_required
def genteachlist(request):
    ret = backend_genteachlist(request.user)
    return render(request, 'oeffcs/GenTeachList.html', ret)

@login_required
def api_timetable_boilerplate(request):
    res = apicall_timetable_boilerplate()
    return JsonResponse(res)

@login_required
def show_timetable_details(request, ttid):
    userobject = Timetable.objects.filter(ttid = ttid)[0].level.user
    ret = display_teacher_list_temp(userobject, ttid)
    if userobject.username != request.user.username:
        ret['warning'] = "This is a shared timetable. Some subjects and teachers may not be available for you. Use at your own risk"
    return render(request, 'oeffcs/TempTeacherList.html', ret)

@login_required
def api_modal_data(request):
    post_data = dict(eval(request.body))
    return JsonResponse(get_timetable_data_by_id(request.user,post_data['ttid'],'second'))

@login_required
def api_loadingscreen(request):
    return JsonResponse(people_status[str(request.user.username)])
    #total, completed, valid

@login_required
def timetable_gen_loading(request):
    time.sleep(0.5)
    return render(request,'oeffcs/TimetableGenLoading.html',people_status[str(request.user.username)])

@login_required
def api_save_preference(request):
    post_data = dict(eval(request.body))
    ttid = post_data['ttid'].strip()
    post_data['ttid'] = ttid
    print(post_data)
    creator = Timetable.objects.filter(ttid = ttid)[0].level.user
    if creator.username == request.user.username:
        form = ChangeStatusForm({'status_value': 5}, instance=request.user.profile)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
        form = ChangeOrderOfTeacher({'save_order': str(post_data)}, instance=request.user.profile)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
        return JsonResponse({})
    else:
        form = ChangeStatusOfShare({'shared_timetable': 1}, instance=request.user.profile)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
        form = ChangeOrderOfTeacher({'save_order': str(post_data)}, instance=request.user.profile)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
        return JsonResponse({})
    # return HttpResponseRedirect('/')

@login_required
def ffcs(request):
    return render(request, "oeffcs/FFCSFinal.html")

def api_win_ffcs(request):
    return JsonResponse({"info":apicall_finalpage(request.user)})