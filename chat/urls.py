from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/add/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/remove/<str:username>/', views.remove_friend, name='remove_friend'),
    
    path('', views.chat_list, name='chat_list'),
    path('<str:username>/', views.chat_room, name='chat_room'),
    path('api/send/<int:room_id>/', views.send_message, name='send_message'),
    path('api/friends/', views.get_friends_api, name='get_friends_api'),
    path('api/share-pin/', views.share_pin_api, name='share_pin_api'),
    path('api/unread-count/', views.get_unread_count, name='get_unread_count'),
]
