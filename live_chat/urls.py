from django.urls import path
from . import views

app_name = 'live_chat'

urlpatterns = [
    # چت آنلاین (AJAX)
    path('start/', views.chat_start, name='chat_start'),
    path('send/', views.chat_send, name='chat_send'),
    path('messages/', views.chat_messages, name='chat_messages'),

    # تیکت — مشتری
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),

    # پنل مدیریت — چت
    path('admin/chats/', views.admin_chat_list, name='admin_chat_list'),
    path('admin/chats/<int:pk>/', views.admin_chat_detail, name='admin_chat_detail'),
    path('admin/chats/<int:pk>/close/', views.admin_chat_close, name='admin_chat_close'),

    # پنل مدیریت — تیکت
    path('admin/tickets/', views.admin_ticket_list, name='admin_ticket_list'),
    path('admin/tickets/<int:pk>/', views.admin_ticket_detail, name='admin_ticket_detail'),
]
