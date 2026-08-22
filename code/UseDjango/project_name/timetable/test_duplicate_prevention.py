"""
Test duplicate prevention for all forms
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from .forms import (
    setup_form, TeacherForm, ClassRoomForm, LabRoomForm,
    yearSetupForm, SubjectForm, PracticalForm,
    TeacherFormSet, ClassRoomFormSet, LabFormSet
)
from .models import (
    setupModel, teacherModel, classRoomModel, labRoomModel,
    yearSetupModel, subjectModel, practicalModel
)


class DepartmentDuplicateTest(TestCase):
    def test_duplicate_department_name(self):
        """Test that duplicate department names are rejected"""
        # Create first department
        setupModel.objects.create(
            department_name='Computer Science',
            start_time='09:00',
            end_time='17:00',
            number_of_days=5
        )
        
        # Try to create second department with same name
        form_data = {
            'department_name': 'Computer Science',
            'start_time': '09:00',
            'end_time': '17:00',
            'number_of_days': 5,
        }
        form = setup_form(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('department_name', form.errors)
    
    def test_duplicate_department_name_case_insensitive(self):
        """Test that duplicate checking is case-insensitive"""
        setupModel.objects.create(
            department_name='Computer Science',
            start_time='09:00',
            end_time='17:00',
            number_of_days=5
        )
        
        form_data = {
            'department_name': 'COMPUTER SCIENCE',  # Different case
            'start_time': '09:00',
            'end_time': '17:00',
            'number_of_days': 5,
        }
        form = setup_form(data=form_data)
        self.assertFalse(form.is_valid())


class TeacherDuplicateTest(TestCase):
    def setUp(self):
        self.department = setupModel.objects.create(
            department_name='CS Dept',
            start_time='09:00',
            end_time='17:00',
            number_of_days=5
        )
    
    def test_duplicate_teacher_in_same_department(self):
        """Test that duplicate teacher names in same department are rejected"""
        # Create first teacher
        teacherModel.objects.create(
            department=self.department,
            teacher_name='Dr. John Smith'
        )
        
        # Try to create second teacher with same name
        teacher = teacherModel(department=self.department)
        form_data = {'teacher_name': 'Dr. John Smith'}
        form = TeacherForm(data=form_data, instance=teacher)
        teacher.department = self.department
        form.instance = teacher
        
        self.assertFalse(form.is_valid())
        self.assertIn('teacher_name', form.errors)


class ClassRoomDuplicateTest(TestCase):
    def setUp(self):
        self.department = setupModel.objects.create(
            department_name='CS Dept',
            start_time='09:00',
            end_time='17:00',
            number_of_days=5
        )
    
    def test_duplicate_classroom_in_same_department(self):
        """Test that duplicate classroom IDs in same department are rejected"""
        classRoomModel.objects.create(
            department=self.department,
            classroom_id='A-101',
            classroom_capacity=60
        )
        
        classroom = classRoomModel(department=self.department)
        form_data = {
            'classroom_id': 'A-101',
            'classroom_capacity': 50
        }
        form = ClassRoomForm(data=form_data, instance=classroom)
        classroom.department = self.department
        form.instance = classroom
        
        self.assertFalse(form.is_valid())
        self.assertIn('classroom_id', form.errors)


class YearDuplicateTest(TestCase):
    def setUp(self):
        self.department = setupModel.objects.create(
            department_name='CS Dept',
            start_time='09:00',
            end_time='17:00',
            number_of_days=5
        )
    
    def test_duplicate_year_in_same_department(self):
        """Test that duplicate year names in same department are rejected"""
        yearSetupModel.objects.create(
            department=self.department,
            year_name='First Year',
            total_students=60,
            number_of_students_in_batch=30
        )
        
        year = yearSetupModel(department=self.department)
        form_data = {
            'year_name': 'First Year',
            'total_students': 50,
            'number_of_students_in_batch': 25
        }
        form = yearSetupForm(data=form_data, instance=year)
        year.department = self.department
        form.instance = year
        
        self.assertFalse(form.is_valid())
        self.assertIn('year_name', form.errors)


class SubjectDuplicateTest(TestCase):
    def setUp(self):
        self.department = setupModel.objects.create(
            department_name='CS Dept',
            start_time='09:00',
            end_time='17:00',
            number_of_days=5
        )
        self.year = yearSetupModel.objects.create(
            department=self.department,
            year_name='First Year',
            total_students=60,
            number_of_students_in_batch=30
        )
        self.teacher = teacherModel.objects.create(
            department=self.department,
            teacher_name='Dr. Smith'
        )
    
    def test_duplicate_subject_in_same_year(self):
        """Test that duplicate subject names in same year are rejected"""
        subject = subjectModel.objects.create(
            year=self.year,
            subject_name='Data Structures',
            hours_per_week=4
        )
        subject.teachers.add(self.teacher)
        
        form_data = {
            'subject_name': 'Data Structures',
            'teachers': [self.teacher.id],
            'hours_per_week': 3
        }
        form = SubjectForm(
            data=form_data,
            department=self.department,
            year=self.year
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('subject_name', form.errors)


class PracticalDuplicateTest(TestCase):
    def setUp(self):
        self.department = setupModel.objects.create(
            department_name='CS Dept',
            start_time='09:00',
            end_time='17:00',
            number_of_days=5
        )
        self.year = yearSetupModel.objects.create(
            department=self.department,
            year_name='First Year',
            total_students=60,
            number_of_students_in_batch=30
        )
        self.teacher = teacherModel.objects.create(
            department=self.department,
            teacher_name='Dr. Smith'
        )
    
    def test_duplicate_practical_in_same_year(self):
        """Test that duplicate practical names in same year are rejected"""
        practical = practicalModel.objects.create(
            year=self.year,
            practical_name='Java Lab',
            hours_per_week=4
        )
        practical.teachers.add(self.teacher)
        
        form_data = {
            'practical_name': 'Java Lab',
            'teachers': [self.teacher.id],
            'hours_per_week': 2
        }
        form = PracticalForm(
            data=form_data,
            department=self.department,
            year=self.year
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('practical_name', form.errors)


print("Duplicate prevention tests created!")
print("Run tests with: python manage.py test timetable.test_duplicate_prevention")
