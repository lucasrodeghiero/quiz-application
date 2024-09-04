from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from teacher import models as TMODEL
from student import models as SMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from django.contrib.auth.models import User

from django.contrib.auth.views import LoginView
from django.contrib import messages

class AdminLoginView(LoginView):
    template_name = 'quiz/adminlogin.html'  # Path to your admin login template

    def form_valid(self, form):
        user = form.get_user()
        
        # Check if the user belongs to the "ADMIN" group
        if user.groups.filter(name='ADMIN').exists():
            return super().form_valid(form)
        else:
            messages.error(self.request, "Only admins can log in here.")
            return redirect('adminlogin')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return self.render_to_response(self.get_context_data(form=form))


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'quiz/index.html')

def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def afterlogin_view(request):
    if is_student(request.user):      
        return redirect('student/student-dashboard')
                
    elif is_teacher(request.user):
        accountapproval=TMODEL.Teacher.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('teacher/teacher-dashboard')
        else:
            return render(request,'teacher/teacher_wait_for_approval.html')
    else:
        return redirect('admin-dashboard')



def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    'total_teacher':TMODEL.Teacher.objects.all().filter(status=True).count(),
    'total_quiz':models.Quiz.objects.all().count(),
    'total_question':models.Question.objects.all().count(),
    }
    return render(request,'quiz/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_teacher_view(request):
    dict={
    'total_teacher':TMODEL.Teacher.objects.all().filter(status=True).count(),
    'pending_teacher':TMODEL.Teacher.objects.all().filter(status=False).count(),
    }
    return render(request,'quiz/admin_teacher.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_teacher_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=True)
    return render(request,'quiz/admin_view_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def update_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=TMODEL.User.objects.get(id=teacher.user_id)
    userForm=TFORM.TeacherUserForm(instance=user)
    teacherForm=TFORM.TeacherForm(request.FILES,instance=teacher)
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=TFORM.TeacherUserForm(request.POST,instance=user)
        teacherForm=TFORM.TeacherForm(request.POST,request.FILES,instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacherForm.save()
            return redirect('admin-view-teacher')
    return render(request,'quiz/update_teacher.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-teacher')




@login_required(login_url='adminlogin')
def admin_view_pending_teacher_view(request):
    teachers= TMODEL.Teacher.objects.all().filter(status=False)
    return render(request,'quiz/admin_view_pending_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
def approve_teacher_view(request, pk):
    if request.method == 'GET':
        teacher = TMODEL.Teacher.objects.get(id=pk)
        teacher.status = True  # Set a default status based on your logic
        teacher.save()
        # Redirect to the current page (assuming it's displaying pending teachers)
        return HttpResponseRedirect('/admin-view-pending-teacher')  # Use request.path for current URL
    
@login_required(login_url='adminlogin')
def reject_teacher_view(request,pk):
    teacher=TMODEL.Teacher.objects.get(id=pk)
    user=User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-pending-teacher')



@login_required(login_url='adminlogin')
def admin_student_view(request):
    dict={
    'total_student':SMODEL.Student.objects.all().count(),
    }
    return render(request,'quiz/admin_student.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'quiz/admin_view_student.html',{'students':students})



@login_required(login_url='adminlogin')
def update_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=SMODEL.User.objects.get(id=student.user_id)
    userForm=SFORM.StudentUserForm(instance=user)
    studentForm=SFORM.StudentForm(request.FILES,instance=student)
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=SFORM.StudentUserForm(request.POST,instance=user)
        studentForm=SFORM.StudentForm(request.POST,request.FILES,instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            return redirect('admin-view-student')
    return render(request,'quiz/update_student.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='adminlogin')
def admin_quiz_view(request):
    return render(request,'quiz/admin_quiz.html')

# @login_required(login_url='adminlogin')
# def admin_add_quiz_view(request):
#     quizForm=forms.QuizForm()
#     if request.method=='POST':
#         quizForm=forms.QuizForm(request.POST)
#         if quizForm.is_valid():        
#             quizForm.save()
#         else:
#             print("form is invalid")
#         return HttpResponseRedirect('/admin-view-quiz')
#     return render(request,'quiz/admin_add_quiz.html',{'quizForm':quizForm})

@login_required(login_url='adminlogin')
def admin_add_quiz_view(request):
    quizForm = forms.QuizForm()
    if request.method == 'POST':
        quizForm = forms.QuizForm(request.POST)
        if quizForm.is_valid():
            quizForm.save()
            return HttpResponseRedirect(reverse('admin-view-quiz'))  # Use reverse to get the URL from the name
        else:
            print("Form is invalid")
    return render(request, 'quiz/admin_add_quiz.html', {'quizForm': quizForm})

@login_required(login_url='adminlogin')
def toggle_quiz_visibility(request, pk):
    quiz = get_object_or_404(models.Quiz, id=pk)
    quiz.is_visible = not quiz.is_visible  # Toggle the visibility
    quiz.save()
    return HttpResponseRedirect(reverse('teacher-view-exam'))


@login_required(login_url='adminlogin')
def admin_view_quiz_view(request):
    quizzes = models.Quiz.objects.all()
    return render(request,'quiz/admin_view_quiz.html',{'quizzes':quizzes})

@login_required(login_url='adminlogin')
def delete_quiz_view(request,pk):
    quiz=models.Quiz.objects.get(id=pk)
    quiz.delete()
    return HttpResponseRedirect('/admin-view-quiz')



@login_required(login_url='adminlogin')
def admin_question_view(request):
    return render(request,'quiz/admin_question.html')

@login_required(login_url='adminlogin')
def admin_add_question_view(request):
    questionForm=forms.QuestionForm()
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            quiz=models.Quiz.objects.get(id=request.POST.get('quizID'))
            question.quiz=quiz
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-question')
    return render(request,'quiz/admin_add_question.html',{'questionForm':questionForm})


@login_required(login_url='adminlogin')
def admin_view_question_view(request):
    quizzes= models.Quiz.objects.all()
    return render(request,'quiz/admin_view_question.html',{'quizzes':quizzes})

@login_required(login_url='adminlogin')
def view_question_view(request,pk):
    questions=models.Question.objects.all().filter(quiz_id=pk)
    return render(request,'quiz/view_question.html',{'questions':questions})

@login_required(login_url='adminlogin')
def delete_question_view(request,pk):
    question=models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/admin-view-question')

@login_required(login_url='adminlogin')
def admin_view_student_marks_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'quiz/admin_view_student_marks.html',{'students':students})

@login_required(login_url='adminlogin')
def admin_view_marks_view(request,pk):
    quizzes = models.Quiz.objects.all()
    response =  render(request,'quiz/admin_view_marks.html',{'quizzes':quizzes})
    response.set_cookie('student_id',str(pk))
    return response

@login_required(login_url='adminlogin')
def admin_check_marks_view(request,pk):
    quiz = models.Quiz.objects.get(id=pk)
    student_id = request.COOKIES.get('student_id')
    student= SMODEL.Student.objects.get(id=student_id)

    results= models.Result.objects.all().filter(exam=quiz).filter(student=student)
    return render(request,'quiz/admin_check_marks.html',{'results':results})
    
def aboutus_view(request):
    return render(request,'quiz/aboutus.html')



