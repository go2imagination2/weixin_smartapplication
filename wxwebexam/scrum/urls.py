from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'home/', views.index, name='index'),
    url(r'single/', views.single, name='single'),
    url(r'answerit/', views.answerit, name='answerit'),
    url(r'enroll_page/', views.enroll_page, name='enroll_page'),
    url(r'enroll/', views.enroll, name='enroll'),
    url(r'scoring/', views.scoring, name='scoring'),
    url(r'h5_main/', views.h5_main, name='h5_main'),
    url(r'h5_main_ex/', views.h5_main_ex, name='h5_main_ex'),
]
