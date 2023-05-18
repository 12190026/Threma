from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('adminlogin/', views.login_admin, name='admin_login'),
    
    path('index/', views.index, name='index'),

    path('executives/', views.executives, name='executives'),

    path('add_member/', views.add_member, name='add_member'),

    path('executivelogin/', views.login_executive, name='executive_login'),

    path('practitioner/', views.practitioner, name='practitioner'),

    path('activity/', views.activity, name='activity'),

    path('profile/', views.profile, name='profile'),

    path('finance/', views.finance, name='finance'),
     
    path('main/', views.main, name='main'),

    path('transferform/', views.transferform, name='transferform'),

    path('add_member_practitioner/', views.add_member_practitioner, name='add_member_practitioner'),

    path('add_activity/', views.add_activity, name='add_activity'),

    path('search-executive-member/', views.search_executive_member, name='search_executive_member'),

    
    path('upload_statement/', views.upload_statement, name='upload_statement'),

    path('update_activity_status/<int:activity_id>/', views.update_activity_status, name='update_activity_status'),

    path('display_member_info/', views.display_member_info, name='display_member_info'),

    #Users
    path('home/', views.home, name='home'),

    path('aboutus/', views.aboutus, name='aboutus'),
] 

# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)