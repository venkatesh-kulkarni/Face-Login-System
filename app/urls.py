from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

app_name = 'home'

urlpatterns = [
    path('',home,name="index"),
    path('signup',signup,name="signup"),
    path('register_face',register_face,name="register_face"),
    path('signin',signin,name="signin"),
    path('logout',signout,name="signout"),
    path('recognize',csrf_exempt(recognize),name="recognize"),
    #path('afterLogin', 'afterLogin.html', name="afterLogin")
]