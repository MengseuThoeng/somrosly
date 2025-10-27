from django.urls import path
from . import views

app_name = 'boards'

urlpatterns = [
    path('', views.board_list, name='list'),
    path('create/', views.board_create, name='create'),
    path('<int:pk>/', views.board_detail, name='detail'),
    path('<int:pk>/edit/', views.board_edit, name='edit'),
    path('<int:pk>/delete/', views.board_delete, name='delete'),
]
