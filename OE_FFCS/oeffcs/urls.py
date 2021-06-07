from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='uploadexcelfile'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('pickteachers/', views.pickteachers, name='pickteachers'),
    path('pickfilters/', views.pickfilters, name='pickfilters'),
    path('precheck/',views.pre_check, name='precheck'),
    path('viewdata/', views.viewdata, name='viewdata'),
]
