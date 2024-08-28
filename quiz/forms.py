from django import forms
from . import models

class QuizForm(forms.ModelForm):
    class Meta:
        model = models.Quiz
        fields = ['quiz_name', 'question_number', 'total_marks', 'is_visible']

class QuestionForm(forms.ModelForm):
    # This will show a dropdown; __str__ method of quiz model is shown in HTML
    # `to_field_name` fetches the corresponding value, user_id present in the quiz model, and returns it
    quizID = forms.ModelChoiceField(queryset=models.Quiz.objects.all(), empty_label="Choose Quiz Name from Dropdown List", to_field_name="id")

    class Meta:
        model = models.Question
        fields = ['quizID', 'marks', 'question', 'option1', 'option2', 'option3', 'option4', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
       
        }

