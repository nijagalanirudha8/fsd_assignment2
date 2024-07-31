# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student_list'),
    path('student_detail/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('register_student/', views.RegisterStudentView.as_view(), name='register_student'),
    path('download_students_pdf/', views.download_students_pdf, name='download_students_pdf'),
    path('download_students_excel/', views.download_students_excel, name='download_students_excel'),
]
