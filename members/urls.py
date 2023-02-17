from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.members, name='members'),
    path('members/details/<lastname>', views.details, name='details'),
    #path('abc')

]