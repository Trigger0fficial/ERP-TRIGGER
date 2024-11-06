from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import *

urlpatterns = [
    path('client_estimate/<int:pk>/', generate_client_estimate, name='client_estimate'),
    path('', show_total_projects, name='total_projects'),
    path('all_projects', show_list_projects, name='all_projects'),
    path('detail_project/<int:pk>/', show_detail_project, name='detail_project'),
    path('login', show_login, name='login'),
    path('register', show_register, name='register'),
    path('create_project', show_create_project, name='create_project'),




]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)