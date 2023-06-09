from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordChangeView
from rest_framework import routers
from .views import ExecutiveMemberViewSet



router = routers.DefaultRouter()

router.register('activities', views.ActivityViewSet)
router.register('executive-members', ExecutiveMemberViewSet)
router.register(r'practitioners', views.PractitionerViewSet)
router.register(r'financial-statements', views.FinancialStatementViewSet)
router.register(r'transfers', views.TransferViewSet)
router.register(r'semsos', views.SemsoViewSet)



urlpatterns = [
    path('api/', include(router.urls)),

    path('adminlogin/', views.login_admin, name='adminlogin'),
    
    path('index/', views.index, name='index'),

    path('executives/', views.executives, name='executives'),

    path('add_member/', views.add_member, name='add_member'),

    path('executivelogin/', views.login_executive, name='executivelogin'),

    path('practitioner/', views.practitioner, name='practitioner'),

    path('activity/', views.activity, name='activity'),

    path('semso/', views.semso, name='semso'),

    path('profile/', views.profile, name='profile'),

    path('finance/', views.finance, name='finance'),
     
    path('main/', views.main, name='main'),

    
    path('edit_activity/<int:activity_id>/', views.edit_activity, name='edit_activity'),

        
    path('activities/<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),

    path('semso/<int:semso_id>/edit/', views.edit_semso, name='edit_semso'),

    path('transferform/', views.transferform, name='transferform'),

    path('add_member_practitioner/', views.add_member_practitioner, name='add_member_practitioner'),

    path('bulk_upload/', views.bulk_upload, name='bulk_upload'),

    path('export_practitioners/', views.export_practitioners, name='export_practitioners'),

    path('semso/<int:semso_id>/delete/', views.delete_semso, name='delete_semso'),

    path('transfer/<int:practitioner>/delete/', views.delete_transfer, name='delete_transfer'),

    path('add_activity/', views.add_activity, name='add_activity'),

    path('add_semso/', views.add_semso, name='add_semso'),

    path('search-executive-member/', views.search_executive_member, name='search_executive_member'),

    path('submit_transfer_form/', views.submit_transfer_form, name='submit_transfer_form'),

    path('edit_statement/<str:year>/', views.edit_statement, name='edit_statement'),

    path('delete_statement/<int:year>/', views.delete_statement, name='delete_statement'),



    path('get-letter/', views.get_letter, name='get-letter'),

    path('view_letter/<int:transfer_id>/', views.view_letter, name='view_letter'),

    path('retrieve_practitioner/', views.retrieve_practitioner, name='retrieve_practitioner'),

    path('change_status/<str:cid>/', views.change_status, name='change_status'),

    path('upload_picture/<str:cid>/', views.upload_picture, name='upload_picture'),

    path('upload_image/', views.upload_image, name='upload_image'),





    
    path('upload_statement/', views.upload_statement, name='upload_statement'),

    path('update_activity_status/<int:activity_id>/', views.update_activity_status, name='update_activity_status'),

    path('display_member_info/', views.display_member_info, name='display_member_info'),

    path('edit_members/<int:member_cid>/edit/', views.edit_member, name='edit_member'),

    path('edit_practitioner/<int:member_cid>/edit/', views.edit_practitioner, name='edit_practitioner'),

    path('members/<int:member_cid>/delete/', views.delete_member, name='delete_member'),

    path('practitioner/<int:member_cid>/delete/', views.delete_practitioner, name='delete_practitioner'),

    path('change_password/', views.change_password, name='change_password'),
    
    path('logout/', views.logout_view, name='logout'),
  

    #Users
    path('', views.home, name='home'),

    path('aboutus/', views.aboutus, name='aboutus'),

    path('uiactivity/', views.uiactivity, name='uiactivity'),

    path('uifinance/', views.uifinance, name='uifinance'),

    path('uisemso/', views.uisemso, name='uisemso'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
