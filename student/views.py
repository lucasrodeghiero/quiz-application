import random
from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from teacher import models as TMODEL

from django.contrib.auth.views import LoginView
from django.contrib import messages


def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    mydict = {'userForm': userForm, 'studentForm': studentForm}
    
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST)
        
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()
    
            student = studentForm.save(commit=False)
            student.user = user
            student.save()
            
            my_student_group, created = Group.objects.get_or_create(name='STUDENT')
            my_student_group.user_set.add(user)
            
            return HttpResponseRedirect('studentlogin')
    return render(request, 'student/studentsignup.html', context=mydict)

class StudentLoginView(LoginView):
    template_name = 'student/studentlogin.html'
    def form_valid(self, form):
        user = form.get_user()
        
        if user.groups.filter(name='STUDENT').exists():
            return super().form_valid(form)
        else:
            messages.error(self.request, "Only students can log in here.")
            return redirect('studentlogin')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return self.render_to_response(self.get_context_data(form=form))


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_quiz':QMODEL.Quiz.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

# @login_required(login_url='studentlogin')
# @user_passes_test(is_student)
# def student_exam_view(request):
#     quizzes=QMODEL.Quiz.objects.all()
#     return render(request,'student/student_exam.html',{'quizzes':quizzes})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    quizzes = QMODEL.Quiz.objects.filter(is_visible=True)
    return render(request, 'student/student_exam.html', {'quizzes': quizzes})


# @login_required(login_url='studentlogin')
# @user_passes_test(is_student)
# def take_exam_view(request,pk):
#     quiz=QMODEL.Quiz.objects.get(id=pk)
#     total_questions=QMODEL.Question.objects.all().filter(quiz=quiz).count()
#     questions=QMODEL.Question.objects.all().filter(quiz=quiz)
#     total_marks=0
#     for q in questions:
#         total_marks=total_marks + q.marks
#     return render(request,'student/take_exam.html',{'quiz':quiz,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request, pk):
    try:
        quiz = QMODEL.Quiz.objects.get(id=pk, is_visible=True)
        questions = QMODEL.Question.objects.filter(quiz=quiz)
        total_questions = questions.count()
        total_marks = sum(q.marks for q in questions)
    except QMODEL.Quiz.DoesNotExist:
        return HttpResponseRedirect(reverse('student_exam_view'))

    return render(request, 'student/take_exam.html', {
        'quiz': quiz,
        'total_questions': total_questions,
        'total_marks': total_marks
    })

# @login_required(login_url='studentlogin')
# @user_passes_test(is_student)
# def start_exam_view(request,pk):
#     quiz=QMODEL.Quiz.objects.get(id=pk)
#     questions=QMODEL.Question.objects.all().filter(quiz=quiz)
#     if request.method=='POST':
#         pass
#     response= render(request,'student/start_exam.html',{'quiz':quiz,'questions':questions})
#     response.set_cookie('quiz_id',quiz.id)
#     return response

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    try:
        quiz = QMODEL.Quiz.objects.get(id=pk, is_visible=True)
        questions = list(QMODEL.Question.objects.filter(quiz=quiz))  # Convert QuerySet to list and shuffle
        random.shuffle(questions)
        
        # Store shuffled question IDs in session to track the order for the answer submission
        request.session['questions_order'] = [q.id for q in questions]

    except QMODEL.Quiz.DoesNotExist:
        return HttpResponseRedirect(reverse('student_exam_view'))
    
    if request.method == 'POST':
        # Add logic for processing answers if needed
        pass
    
    response = render(request, 'student/start_exam.html', {'quiz': quiz, 'questions': questions})
    response.set_cookie('quiz_id', quiz.id)
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    quiz_id = request.COOKIES.get('quiz_id')
    if quiz_id:
        quiz = QMODEL.Quiz.objects.get(id=quiz_id)
        question_ids = request.session.get('questions_order', [])
        total_marks = 0
        
        for i, question_id in enumerate(question_ids):
            question = QMODEL.Question.objects.get(id=question_id)
            selected_ans = request.COOKIES.get(str(i + 1))
            if selected_ans == question.answer:
                total_marks += question.marks
        
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks = total_marks
        result.exam = quiz
        result.student = student
        result.save()

        return HttpResponseRedirect('view-result')




@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    quizzes=QMODEL.Quiz.objects.all()
    return render(request,'student/view_result.html',{'quizzes':quizzes})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    quiz=QMODEL.Quiz.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=quiz).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    quizzes=QMODEL.Quiz.objects.all()
    return render(request,'student/student_marks.html',{'quizzes':quizzes})
  