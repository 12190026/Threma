from django.urls import path
from . import views

urlpatterns = [
    path('adminlogin/', views.login_admin, name='admin_login'),
    
    path('index/', views.index, name='index'),

    path('executives/', views.executives, name='executives'),

    path('add_member/', views.add_member, name='add_member'),

    path('executivelogin/', views.login_executive, name='executive_login'),

    path('practitioner/', views.practitioner, name='practitioner'),

    path('add_member_practitioner/', views.add_member_practitioner, name='add_member_practitioner'),

    path('home/', views.home, name='home'),
]