from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list, name='list'),
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
    path('api/recent/', views.get_recent_notifications, name='recent'),
    path('api/<int:notification_id>/read/', views.mark_as_read, name='mark_read'),
    path('api/mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
]
