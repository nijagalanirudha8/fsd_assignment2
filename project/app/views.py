import io
import pandas as pd
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Student, Course
from django.views.generic import FormView, DetailView, ListView
from . forms import StudentForm
from django.http import JsonResponse

class StudentDetailView(DetailView):
    model = Student
    template_name = 'app/student_detail.html'
    context_object_name = 'students'

class StudentListView(ListView):
    model = Student
    template_name = 'app/student_list.html'
    context_object_name = 'studentlist'

class RegisterStudentView(FormView):
    template_name = 'app/register_student.html'
    form_class = StudentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        return context

    def form_valid(self, form):
        student = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "message": "Profile created successfully for " + form.cleaned_data.get('name'),
                "student": {
                    "name": student.name,
                    "usn": student.usn,
                    "courses": [course.name for course in student.courses.all()]
                }
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"errors": form.errors}, status=400)
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def download_students_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica", 12)
    students = Student.objects.all()
    p.drawString(100, 750, "Student List")

    y = 720
    for student in students:
        courses = ", ".join([course.name for course in student.courses.all()])
        p.drawString(100, y, f"Name: {student.name}, USN: {student.usn}, Courses: {courses}")
        y -= 20
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750

    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="students.pdf"'
    return response

def download_students_excel(request):
    students = Student.objects.all()
    data = []
    for student in students:
        courses = ", ".join([course.name for course in student.courses.all()])
        data.append({
            "Name": student.name,
            "USN": student.usn,
            "Courses": courses,
        })

    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
    return response
