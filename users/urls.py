from django.urls import path
from .import views

urlpatterns= [

    path("",views.main_page,name=""),
    path("home",views.home,name="home"),
]