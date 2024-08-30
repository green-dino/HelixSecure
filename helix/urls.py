from django.urls import path
from . import views

app_name = 'helix'

urlpatterns = [
    path('', views.ControlListView.as_view(), name='control_list'),
    path('control/<int:pk>/', views.ControlDetailView.as_view(), name='control_detail'),
    path('control/create/', views.ControlCreateView.as_view(), name='control_create'),
    path('control/<int:pk>/update/', views.ControlUpdateView.as_view(), name='control_update'),
    path('control/<int:pk>/delete/', views.ControlDeleteView.as_view(), name='control_delete'),
]