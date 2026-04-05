from django.urls import path
from .views import RegisterView
from .views import UserListView, toggle_admin
from .views import edit_comment, delete_comment
from .views import mark_done
from .views import NotificationListView
from .views import (
    TaskListView,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    TaskDetailView,
    add_task_admin,
    remove_task_admin
)

from .views import (
    TaskListView,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    TaskDetailView
)

urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('create/', TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('<int:pk>/update/', TaskUpdateView.as_view(), name='task_update'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/toggle-admin/', toggle_admin, name='toggle_admin'),
    path('task/<int:task_id>/add-admin/<int:user_id>/', add_task_admin, name='add_task_admin'),
    path('task/<int:task_id>/remove-admin/<int:user_id>/', remove_task_admin, name='remove_task_admin'),
    path('comment/<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('<int:pk>/done/', mark_done, name='task_done'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
]