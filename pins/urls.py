from django.urls import path
from . import views

app_name = 'pins'

urlpatterns = [
    path('', views.pin_list, name='list'),
    path('create/', views.pin_create, name='create'),
    path('<int:pk>/', views.pin_detail, name='detail'),
    path('<int:pk>/edit/', views.pin_edit, name='edit'),
    path('<int:pk>/delete/', views.pin_delete, name='delete'),
    path('<int:pk>/like/', views.pin_like, name='like'),
    path('<int:pin_pk>/save-to-board/<int:board_pk>/', views.save_to_board, name='save_to_board'),
    path('<int:pk>/report/', views.report_pin, name='report'),
    
    # Comment URLs
    path('<int:pk>/comments/add/', views.add_comment, name='add_comment'),
    path('<int:pk>/comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<int:pk>/comments/<int:comment_id>/like/', views.like_comment, name='like_comment'),
]
