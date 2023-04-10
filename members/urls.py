from django.shortcuts import render
from django.urls import path
from . import views

from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('main/', views.main, name='main'),
    path('members/', views.members, name='members'),
    path('members/details/<int:id>', views.details, name='details'),
    path('members/details/<int:id>/moncompte/', views.moncompte, name='moncompte'),
    path('testing/', views.testing, name='testing'),
    path('testtest/', views.testtest, name='testtest'),
    path('', views.loginPage, name='login'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('recherche/', views.recherche, name='recherche')
]
