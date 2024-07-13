from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('phone_verification/', views.verify_phone, name='verification'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('resend-code/', views.resend_code, name='resend_code'),
    path('change-number/', views.change_number, name='change_number'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('whatsapp/', views.whatsapp, name='whatsapp'),
    path('whatsappUser/', views.whatsappUser, name='whatsappUser'),
    path('chatgpt/', views.chatgpt, name='chatgpt'),
    path('email/', views.email, name='email'),
    path('callback_url', views.callback_view, name='callback_url'),
    path('docs/', views.docs, name='docs'),
    path('logout/', views.logout_user, name='logOut'),

    path('generate_token/', views.generate_token, name='generate_token'),
    # path('whatsapp_api/<str:token>/<str:to>/<str:message>/', views.whatsapp_api, name='whatsapp_api'),
    path('chatgpt_api/', views.chatgpt_api, name='chatgpt_api'),

]