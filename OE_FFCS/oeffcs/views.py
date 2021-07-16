from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, request, response
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
from discord_logger import DiscordLogger
from ipware import get_client_ip

options_info = {
    "application_name": "OEFFCS LOGGER",
    "service_name": "Backend logger",
    "service_icon_url": "https://cdn.discordapp.com/attachments/853138859772215299/865220535964925952/unknown.png",
    "display_hostname": False,
    "default_level": "info",
}
options_success = {
    "application_name": "OEFFCS LOGGER",
    "service_name": "Backend logger",
    "service_icon_url": "https://cdn.discordapp.com/attachments/853138859772215299/865220535964925952/unknown.png",
    "display_hostname": False,
    "default_level": "success",
}
options_error = {
    "application_name": "OEFFCS LOGGER",
    "service_name": "Backend logger",
    "service_icon_url": "https://cdn.discordapp.com/attachments/853138859772215299/865220535964925952/unknown.png",
    "display_hostname": False,
    "default_level": "error",
}

lowlevellog_info = DiscordLogger(webhook_url="https://discord.com/api/webhooks/865251088046489630/OQlPSvuqHFdTepq37bm0q4cffe8HrA3CzjlqH-0NZDuCZnmztyTYtYdD9DzVFqGatTNx", **options_info)
highlevellog_info = DiscordLogger(webhook_url="https://discord.com/api/webhooks/865266449731420241/enyFO8HDsx3gQwvXYcrUZ2WilDkSKm3EnfjmEpknR4yFOtyYAnqK1fczycvzPPN2ihgj", **options_info)
lowlevellog_success = DiscordLogger(webhook_url="https://discord.com/api/webhooks/865251088046489630/OQlPSvuqHFdTepq37bm0q4cffe8HrA3CzjlqH-0NZDuCZnmztyTYtYdD9DzVFqGatTNx", **options_success)
highlevellog_success = DiscordLogger(webhook_url="https://discord.com/api/webhooks/865266449731420241/enyFO8HDsx3gQwvXYcrUZ2WilDkSKm3EnfjmEpknR4yFOtyYAnqK1fczycvzPPN2ihgj", **options_success)
lowlevellog_error = DiscordLogger(webhook_url="https://discord.com/api/webhooks/865251088046489630/OQlPSvuqHFdTepq37bm0q4cffe8HrA3CzjlqH-0NZDuCZnmztyTYtYdD9DzVFqGatTNx", **options_error)
highlevellog_error = DiscordLogger(webhook_url="https://discord.com/api/webhooks/865266449731420241/enyFO8HDsx3gQwvXYcrUZ2WilDkSKm3EnfjmEpknR4yFOtyYAnqK1fczycvzPPN2ihgj", **options_error)

# logger.construct(title="Log", description="Service restarted!")
# response = logger.send()

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
    ip, is_routable = get_client_ip(request)
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
            # print("I'm here")
            form.instance.user = request.user
            form.save()
        message = request.user.username+' ('+ip+') has uploaded excel sheet '+str(request.user.profile.data_file)
        highlevellog_success.construct(title="Progress Log", description=message)
        response = highlevellog_success.send()
        return HttpResponseRedirect('/')
        # except User.profile.RelatedObjectDoesNotExist:
        #     form = UploadFileForm(request.POST, request.FILES)
        #     if form.is_valid():
        #         # file is saved
        #         form.instance.user = request.userz
        #         form.save()
        #         return HttpResponseRedirect('/oeffcs')
    else:
        message = request.user.username+' ('+ip+') has entered Upload File page!'
        highlevellog_info.construct(title="Page View Log", description=message)
        response = highlevellog_info.send()
        form = UploadFileForm()
    return render(request, 'oeffcs/uploadexcel.html', {'form': form})


@login_required
def pickteachers(request):
    # teacherdata = str(request.user.profile.data_file)
    ip, is_routable = get_client_ip(request)
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
            message = request.user.username+' ('+ip+')'+' has chosen teachers! \nTeachers chosen = '+json.dumps(postdata_cleaned, indent=3)
            highlevellog_success.construct(title="Progress Log", description=message)
            highlevellog_success.send()
            return HttpResponseRedirect('/timetablesgenerating/')
    
    message = request.user.username+' ('+ip+')'+' has entered the Pick Teachers page!'
    highlevellog_info.construct(title="Page View Log", description=message)
    highlevellog_info.send()
    return render(request, 'oeffcs/pickteachers.html', {'teacherdata': ret, 'errordisplay': ''})


@login_required
def pickfilters(request):
    ip, is_routable = get_client_ip(request)
    message = request.user.username+' ('+ip+')'+' has entered the Pick Filters page!'
    highlevellog_info.construct(title="Page View Log", description=message)
    highlevellog_info.send()
    teacherdata = json.loads(request.user.profile.saveteachers)
    return render(request, 'oeffcs/pickfilters.html', {'display': teacherdata})

@login_required
def pre_check(request):
    ip, is_routable = get_client_ip(request)
    data=dict(eval(request.body))
    return_data = query_database(data, request.user)
    message = request.user.username+' ('+ip+')'+' made a pre-check call for '+str(len(return_data))+' timetables with \
        filters: \n'+json.dumps(data, indent=3)
    lowlevellog_success.construct(title="Progress Log", description=message)
    lowlevellog_success.send()
    return JsonResponse(data={"ret":len(return_data)})

@login_required
def viewdata(request):
    ip, is_routable = get_client_ip(request)
    message = request.user.username+' ('+ip+')'+' has entered the Dashboard!'
    highlevellog_info.construct(title="Page View Log", description=message)
    highlevellog_info.send()
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
    ip, is_routable = get_client_ip(request)
    filters = dict(request.POST)
    del filters['csrfmiddlewaretoken']
    savefilters(filters, request.user)
    message = request.user.username+' ('+ip+')'+' saved filters: \n'+json.dumps(filters, indent=3)
    highlevellog_success.construct(title="Progress Log", description=message)
    highlevellog_success.send()
    return HttpResponseRedirect('/')

@login_required
def tablepriority(request):
    ip, is_routable = get_client_ip(request)
    message = request.user.username+' ('+ip+')'+' has entered the Table Priority Page!'
    highlevellog_info.construct(title="Page View Log", description=message)
    highlevellog_info.send()
    # ret = apicall_getselectedtt(request.user)
    ret = apicall_render_next(request.user, 0, 'first')
    return render(request, 'oeffcs/TablePriority.html', ret)

@login_required
def api_render_tt(request):
    post_data = dict(eval(request.body))
    ret = apicall_render_next(request.user, post_data['index'])
    ip, is_routable = get_client_ip(request)
    lowlevellog_info.construct(title="Api Log", description=request.user.username+" ("+ip+") called api_render_tt api call. Data: \n"+json.dumps(ret, indent=2))
    response = lowlevellog_info.send()
    return JsonResponse(ret)

@login_required
def api_score_change(request):
    post_data = dict(eval(request.body))
    ttid = apicall_changepriority_by_id(request.user, post_data['index'], post_data['score'])
    ip, is_routable = get_client_ip(request)
    message = request.user.username+' ('+ip+')'+' has changed priority of table '+ttid+' to '+str(post_data['score'])+'!'
    highlevellog_success.construct(title="Progress Log", description=message)
    highlevellog_success.send()
    post_data['ttid'] = ttid
    lowlevellog_info.construct(title="Api Log", description=request.user.username+" ("+ip+") called api_score_change api call. Data:\n"+json.dumps(post_data, indent=2))
    response = lowlevellog_info.send()
    return JsonResponse({})

@login_required
def api_nickname_change(request):
    post_data = dict(eval(request.body))
    ttid = apicall_changenick_by_id(request.user, post_data['index'], post_data['nick'])
    ip, is_routable = get_client_ip(request)
    message = request.user.username+' ('+ip+')'+' has changed nickname of table '+ttid+' to '+post_data['nick']+'!'
    highlevellog_success.construct(title="Progress Log", description=message)
    highlevellog_success.send()
    post_data['ttid'] = ttid
    lowlevellog_info.construct(title="Api Log", description=request.user.username+" ("+ip+") called api_nickname_change api call. Data:\n"+json.dumps(post_data, indent=2))
    response = lowlevellog_info.send()
    return JsonResponse({})

@login_required
def genteachlist(request):
    ip, is_routable = get_client_ip(request)
    message = request.user.username+' ('+ip+')'+' has entered the Generate Teacher List page'
    highlevellog_info.construct(title="Page View Log", description=message)
    highlevellog_info.send()
    ret = backend_genteachlist(request.user)
    return render(request, 'oeffcs/GenTeachList.html', ret)

@login_required
def api_timetable_boilerplate(request):
    res = apicall_timetable_boilerplate()
    ip, is_routable = get_client_ip(request)
    lowlevellog_info.construct(title="Api Log", description=request.user.username+" ("+ip+") requested api_timetable_boilerplate")
    response = lowlevellog_info.send()
    return JsonResponse(res)

@login_required
def show_timetable_details(request, ttid):
    ip, is_routable = get_client_ip(request)
    
    userobject = Timetable.objects.filter(ttid = ttid)[0].level.user
    ret = display_teacher_list_temp(userobject, ttid)
    if userobject.username != request.user.username:
        ret['warning'] = "This is a shared timetable. Some subjects and teachers may not be available for you. Use at your own risk"
        message = request.user.username+' ('+ip+')'+'has entered the Subject Priority (Temporary Teacher list) page of ttid '+ttid+'! (SHARED TIMETABLE)'
        highlevellog_info.construct(title="Page View Log", description=message)
        highlevellog_info.send()
    else:
        message = request.user.username+' ('+ip+')'+'has entered the Subject Priority (Temporary Teacher list) page of ttid '+ttid+'!'
        highlevellog_info.construct(title="Page View Log", description=message)
        highlevellog_info.send()
    return render(request, 'oeffcs/TempTeacherList.html', ret)

@login_required
def api_modal_data(request):
    post_data = dict(eval(request.body))
    ip, is_routable = get_client_ip(request)
    lowlevellog_info.construct(title="Api Log", description=request.user.username+" ("+ip+") called api_modal_data")
    response = lowlevellog_info.send()
    return JsonResponse(get_timetable_data_by_id(request.user,post_data['ttid'],'second'))

@login_required
def api_loadingscreen(request):
    try:
        ip, is_routable = get_client_ip(request)
        lowlevellog_info.construct(title="Api Log", description=request.user.username+" ("+ip+") is on loading screen")
        response = lowlevellog_info.send()
        return JsonResponse(people_status[str(request.user.username)])
        
    #total, completed, valid
    except KeyError:
        ip, is_routable = get_client_ip(request)
        lowlevellog_error.construct(title="Api Log", description=request.user.username+" ("+ip+") caught error on loading screen! Restarting!")
        response = lowlevellog_error.send()
        threadsplit = threading.Thread(target = generate_time_tables, args = (request.user,))
        threadsplit.start()
        return JsonResponse(people_status[str(request.user.username)])

@login_required
def timetable_gen_loading(request):
    time.sleep(0.5)
    ip, is_routable = get_client_ip(request)
    try:
        message = request.user.username+' ('+ip+')'+' has entered the Loading Screen with stats '+json.dumps(people_status[str(request.user.username)],indent=3)+'!'
        highlevellog_info.construct(title="Page View Log", description=message)
        highlevellog_info.send()
        return render(request,'oeffcs/TimetableGenLoading.html',people_status[str(request.user.username)])
    except KeyError:
        threadsplit = threading.Thread(target = generate_time_tables, args = (request.user,))
        threadsplit.start()
        time.sleep(0.5)
        message = request.user.username+' ('+ip+')'+' has entered the Loading Screen with an error, Now reloading. \nStats: '+json.dumps(people_status[str(request.user.username)],indent=3)+'!'
        highlevellog_error.construct(title="Page View Log", description=message)
        highlevellog_error.send()
        return render(request,'oeffcs/TimetableGenLoading.html',people_status[str(request.user.username)])

@login_required
def api_save_preference(request):
    post_data = dict(eval(request.body))
    ttid = post_data['ttid'].strip()
    post_data['ttid'] = ttid
    ip, is_routable = get_client_ip(request)
    message = request.user.username+' ('+ip+')'+' has saved ttid '+ttid+' for thier Win FFCS Page!'
    highlevellog_success.construct(title="Progress Log", description=message)
    highlevellog_success.send()
    # print(post_data)
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
    ip, is_routable = get_client_ip(request)
    message = request.user.username+' ('+ip+')'+' has entered the Win FFCS page!'
    highlevellog_info.construct(title="Page View Log", description=message)
    highlevellog_info.send()
    return render(request, "oeffcs/FFCSFinal.html")

@login_required
def api_win_ffcs(request):
    return JsonResponse({"info":apicall_finalpage(request.user)})

@login_required
def api_lowlevel_info(request):
    data = dict(eval(request.body))
    message = data['message']
    title = data['title']
    lowlevellog_info.construct(title=title, description=message)
    lowlevellog_info.send()

@login_required
def api_lowlevel_success(request):
    data = dict(eval(request.body))
    message = data['message']
    title = data['title']
    lowlevellog_success.construct(title=title, description=message)
    lowlevellog_success.send()

@login_required
def api_lowlevel_error(request):
    data = dict(eval(request.body))
    message = data['message']
    title = data['title']
    lowlevellog_error.construct(title=title, description=message)
    lowlevellog_error.send()