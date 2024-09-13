# Project README

## Functions

### Admin
- **Create Admin Account:**
  - Use the command:
    ```bash
    py manage.py createsuperuser
    ```
- **Dashboard:**
  - View total numbers of students, teachers, quizzes, and questions.
- **Manage Teachers:**
  - View, update, delete, and approve teacher accounts.
- **Manage Students:**
  - View, update, and delete student accounts.
  - View student marks.
- **Manage Quizzes/Exams:**
  - Add, view, and delete quizzes/exams.
  - Add questions to respective quizzes with options, correct answers, and marks.
  - View and delete questions.

### Teacher
- **Application and Login:**
  - Apply for a position. Login is permitted after admin approval.
- **Dashboard:**
  - View total numbers of students, quizzes, and questions.
- **Manage Quizzes/Exams:**
  - Add, view, and delete quizzes/exams.
  - Add questions to respective quizzes with options, correct answers, and marks.
  - View and delete questions.

> **Note:** Admins are responsible for hiring teachers to manage quizzes and questions.

### Student
- **Account Creation and Login:**
  - Create an account without admin approval and login immediately after signup.
- **Dashboard:**
  - View total numbers of quizzes/exams and questions.
- **Take Quiz:**
  - Take any quiz at any time with no limit on the number of attempts.
  - View marks for each attempt of each exam.
- **Question Format:**
  - Questions follow an MCQ pattern with 4 options and 1 correct answer.

## How to Run This Project

1. **Install Python (version 3.7.6):**
   - Ensure to check "Add to Path" during installation.
2. **Install Required Packages:**
   - Open a terminal and execute:
     ```bash
     python -m pip install -r requirements.txt
     ```
3. **Download and Extract Project:**
   - Download the project zip folder and extract it.
4. **Run the Project:**
   - Navigate to the project folder in the terminal and execute the following commands:
     ```bash
     py manage.py makemigrations
     py manage.py migrate
     py manage.py runserver
     ```
5. **Access the Application:**
   - Open your browser and enter the following URL:
     ```bash
     http://127.0.0.1:8000/
     ```

## Drawbacks/LoopHoles
- Admins/teachers can add any number of questions to a quiz, but while adding a quiz, the admin must specify the number of questions.
