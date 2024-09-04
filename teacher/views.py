from django.shortcuts import get_object_or_404, render, redirect
from . import forms,models
from django.urls import reverse, path
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from student import models as SMODEL
from quiz import forms as QFORM
from quiz.forms import QuizForm
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import User






@login_required(login_url='teacherlogin')
def teacher_view_student_marks_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'teacher/teacher_view_student_marks.html',{'students':students})

@login_required(login_url='teacherlogin')
def teacher_view_marks_view(request,pk):
    quizzes = QMODEL.Quiz.objects.all()
    response =  render(request,'teacher/teacher_view_marks.html',{'quizzes':quizzes})
    response.set_cookie('student_id',str(pk))
    return response


    
@login_required(login_url='teacherlogin')
def teacher_check_marks_view(request, pk):
    # Retrieve the Quiz instance using get() instead of all()
    quiz = QMODEL.Quiz.objects.get(id=pk)
    
    # Get the student from cookies
    student_id = request.COOKIES.get('student_id')
    student = SMODEL.Student.objects.get(id=student_id)

    # Filter results by quiz and student
    results = QMODEL.Result.objects.filter(exam=quiz, student=student)
    
    return render(request, 'teacher/teacher_check_marks.html', {'results': results})

def aboutus_view(request):
    return render(request,'quiz/aboutus.html')






def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict={
    
    'total_quiz':QMODEL.Quiz.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    'total_student':SMODEL.Student.objects.all().count()
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')


# @login_required(login_url='teacherlogin')
# @user_passes_test(is_teacher)
# def teacher_add_exam_view(request):
#     quizForm = QFORM.QuizForm()  # Use the correct form name here
#     if request.method == 'POST':
#         quizForm = QFORM.QuizForm(request.POST)
#         if quizForm.is_valid():        
#             quizForm.save()
#         else:
#             print("Form is invalid")
#         return HttpResponseRedirect('/teacher/teacher-view-exam')
#     return render(request, 'teacher/teacher_add_exam.html', {'quizForm': quizForm})

def teacher_add_exam_view(request):
    quizForm = QuizForm()
    if request.method == 'POST':
        quizForm = QuizForm(request.POST)
        if quizForm.is_valid():
            quizForm.save()
            return HttpResponseRedirect('/teacher/teacher-view-exam')
        else:
            print("Form is invalid")
    return render(request, 'teacher/teacher_add_exam.html', {'quizForm': quizForm})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    quizzes = QMODEL.Quiz.objects.all()
    return render(request,'teacher/teacher_view_exam.html',{'quizzes':quizzes})

# @login_required(login_url='teacherlogin')
# def toggle_quiz_visibility(request, pk):
#     quiz = get_object_or_404(models.Quiz, id=pk)
#     quiz.is_visible = not quiz.is_visible  # Toggle the visibility
#     quiz.save()
#     return HttpResponseRedirect(reverse('teacher-view-exam'))

@login_required(login_url='teacherlogin')
def toggle_quiz_visibility(request, pk):
    quiz = get_object_or_404(models.Quiz, id=pk)
    quiz.is_visible = not quiz.is_visible
    quiz.save()
    return HttpResponseRedirect(reverse('teacher-view-exam'))


  
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    quiz=QMODEL.Quiz.objects.get(id=pk)
    quiz.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='teacherlogin')
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm=QFORM.QuestionForm()
    if request.method=='POST':
        questionForm=QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            quiz=QMODEL.Quiz.objects.get(id=request.POST.get('quizID'))
            question.quiz=quiz
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request,'teacher/teacher_add_question.html',{'questionForm':questionForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    quizzes= QMODEL.Quiz.objects.all()
    return render(request,'teacher/teacher_view_question.html',{'quizzes':quizzes})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(quiz_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')


@login_required(login_url='teacherlogin')
def teacher_view_student(request):
    students= SMODEL.Student.objects.all()
    return render(request,'teacher/teacher_view_student.html',{'students':students})


@login_required(login_url='teacherlogin')
def delete_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/teacher/teacher-view-student')

@login_required(login_url='teacherlogin')
def delete_question_view(request,pk):
    question=QMODEL.Question.objects.all().filter(quiz_id=pk)
    question.delete()
    return render(request,'teacher/see_question.html',{'question':question})