from django.contrib import admin
from django.urls import include, path
from django.urls import path
from django.contrib.auth.views import LoginView

from . import views


urlpatterns = [
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('accounts/profile/', views.profile, name='profile'),
    path('classification/', views.classification, name='classification'),
    path('calendar/', views.calendar, name='calendar'),
    path('driver/', views.driver, name='driver'),
    path('gpinfo/', views.gpinfo, name='gpinfo'),
    path('gpinfo/<int:ano>/', views.gpinfo2, name='gpinfo2'),
    path('gpinfo/<int:ano>/<str:circuit>/', views.gpinfo3, name='gpinfo3'),
    path('gpinfo/<int:ano>/<str:circuit>/<str:driver>/', views.driverinfo, name='driverinfo'),
    path('comparation/', views.comparation, name='comparation'),
    path('comparation/<int:ano>/', views.comparation2, name='comparation2'),
    path('speed/', views.speed,name='speed'),
    path('speed/<int:ano>/', views.speed2, name='speed2'),
    path('about/', views.about, name='about')
]
