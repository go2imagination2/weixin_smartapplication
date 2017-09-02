from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'single/', views.single, name='single'),
    url(r'multi/', views.multi, name='multi'),
]
