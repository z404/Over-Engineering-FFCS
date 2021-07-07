from django.urls import path
from . import views

urlpatterns = [
    path('', views.viewdata, name='index'),
    path('upload/', views.upload_file, name='uploadexcelfile'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('pickteachers/', views.pickteachers, name='pickteachers'),
    path('pickfilters/', views.pickfilters, name='pickfilters'),
    path('precheck/',views.pre_check, name='precheck'),
    path('viewdata/', views.viewdata, name='viewdata'),
    path('savefilters/', views.save_filters, name='savefilters'),
    path('timetablepriority/',views.tablepriority, name='tablepriority'),
    path('rendertimetable/',views.api_render_tt, name='rendertimetable'),
    path('scorechange/',views.api_score_change, name='scorechange'),
    path('nicknamechange/',views.api_nickname_change, name='nicknamechange'),
    path('genteachlist/',views.genteachlist, name='genteachlist'),
    path('timetableboilerplate/',views.api_timetable_boilerplate, name='timetableboilerplate'),
    path('showtimetable/<ttid>/',views.show_timetable_details, name='showtimetable'),
    path('modaldata/', views.api_modal_data, name='modaldata'),
    path('timetablesgenerating/',views.timetable_gen_loading, name='timetablesgenerating'),
    path('loadingscreenstatus/', views.api_loadingscreen, name='loadingscreenstatus'),
    path('savepreference/', views.api_save_preference, name='savepreference'),
]
