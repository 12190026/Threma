from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('adminlogin/', views.login_admin, name='admin_login'),
    
    path('index/', views.index, name='index'),

    path('executives/', views.executives, name='executives'),

    path('add_member/', views.add_member, name='add_member'),

    path('executivelogin/', views.login_executive, name='executive_login'),

    path('practitioner/', views.practitioner, name='practitioner'),

    path('activity/', views.activity, name='activity'),

    path('semso/', views.semso, name='semso'),

    path('profile/', views.profile, name='profile'),

    path('finance/', views.finance, name='finance'),
     
    path('main/', views.main, name='main'),

    path('transferform/', views.transferform, name='transferform'),

    path('add_member_practitioner/', views.add_member_practitioner, name='add_member_practitioner'),

    path('add_activity/', views.add_activity, name='add_activity'),

    path('add_semso/', views.add_semso, name='add_semso'),

    path('search-executive-member/', views.search_executive_member, name='search_executive_member'),

    path('submit_transfer_form/', views.submit_transfer_form, name='submit_transfer_form'),

    
    path('upload_statement/', views.upload_statement, name='upload_statement'),

    path('update_activity_status/<int:activity_id>/', views.update_activity_status, name='update_activity_status'),

    path('display_member_info/', views.display_member_info, name='display_member_info'),

    path('edit_members/<int:member_cid>/edit/', views.edit_member, name='edit_member'),

    path('edit_practitioner/<int:member_cid>/edit/', views.edit_practitioner, name='edit_practitioner'),

    path('members/<int:member_cid>/delete/', views.delete_member, name='delete_member'),

    path('practitioner/<int:member_cid>/delete/', views.delete_practitioner, name='delete_practitioner'),

    path('change_password/', views.change_password, name='change_password'),

    path('change-password/', PasswordChangeView.as_view(template_name='change_password.html'), name='password_change'),

    path('logout/', views.logout_view, name='logout'),
  

    #Users
    path('home/', views.home, name='home'),

    path('aboutus/', views.aboutus, name='aboutus'),

    path('uiactivity/', views.uiactivity, name='uiactivity'),

    path('uifinance/', views.uifinance, name='uifinance'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
