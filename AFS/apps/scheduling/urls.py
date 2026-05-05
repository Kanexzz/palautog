from django.urls import path
from . import views

urlpatterns = [
    path('faculty/', views.FacultyListView.as_view(), name='faculty_list'),
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('sections/', views.SectionListView.as_view(), name='section_list'),
    path('teaching-load/', views.TeachingLoadView.as_view(), name='teaching_load'),
    path('generate/', views.ScheduleGeneratorView.as_view(), name='schedule_generate'),
    path('', views.ScheduleListView.as_view(), name='schedule_list'),
    path('section-schedule/', views.SectionScheduleView.as_view(), name='section_schedule'),
    path('<int:pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
]
