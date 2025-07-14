from django.urls import path

from .views import ProjectListCreateView, ProjectDetailView, AddMemberView




urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<uuid:project_id>/add_member/', AddMemberView.as_view(), name='add-member'),
]
