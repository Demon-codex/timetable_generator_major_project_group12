"""
Test validation for all forms to ensure they work correctly
and don't break existing functionality
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import time
from .forms import (
    setup_form, RecessForm, TeacherForm, ClassRoomForm, LabRoomForm,
    yearSetupForm, SubjectForm, PracticalForm
)
from .models import setupModel, teacherModel


class SetupFormValidationTest(TestCase):
    def test_valid_setup_form(self):
        """Test that valid data passes"""
        form_data = {
            'department_name': 'Computer Science',
            'start_time': '09:00',
            'end_time': '17:00',
            'number_of_days': 5,
        }
        form = setup_form(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_end_time_before_start_time(self):
        """Test that end time must be after start time"""
        form_data = {
            'department_name': 'IT',
            'start_time': '17:00',
            'end_time': '09:00',  # Invalid: before start_time
            'number_of_days': 5,
        }
        form = setup_form(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_empty_department_name(self):
        """Test that department name cannot be empty"""
        form_data = {
            'department_name': '  ',  # Empty after strip
            'start_time': '09:00',
            'end_time': '17:00',
            'number_of_days': 5,
        }
        form = setup_form(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_invalid_number_of_days(self):
        """Test that number of days must be 1-7"""
        form_data = {
            'department_name': 'CS',
            'start_time': '09:00',
            'end_time': '17:00',
            'number_of_days': 10,  # Invalid: > 7
        }
        form = setup_form(data=form_data)
        self.assertFalse(form.is_valid())


class YearSetupFormValidationTest(TestCase):
    def test_valid_year_form(self):
        """Test that valid data passes"""
        form_data = {
            'year_name': 'First Year',
            'total_students': 60,
            'number_of_students_in_batch': 30,
        }
        form = yearSetupForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_batch_size_greater_than_total(self):
        """Test that batch size cannot exceed total students"""
        form_data = {
            'year_name': 'Second Year',
            'total_students': 50,
            'number_of_students_in_batch': 60,  # Invalid: > total
        }
        form = yearSetupForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_zero_students(self):
        """Test that zero students is invalid"""
        form_data = {
            'year_name': 'Third Year',
            'total_students': 0,  # Invalid
            'number_of_students_in_batch': 0,
        }
        form = yearSetupForm(data=form_data)
        self.assertFalse(form.is_valid())


class ClassRoomFormValidationTest(TestCase):
    def test_valid_classroom(self):
        """Test that valid data passes"""
        form_data = {
            'classroom_id': 'A-101',
            'classroom_capacity': 60,
        }
        form = ClassRoomForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_zero_capacity(self):
        """Test that zero capacity is invalid"""
        form_data = {
            'classroom_id': 'B-202',
            'classroom_capacity': 0,  # Invalid
        }
        form = ClassRoomForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_unrealistic_capacity(self):
        """Test that capacity > 500 is rejected"""
        form_data = {
            'classroom_id': 'C-303',
            'classroom_capacity': 600,  # Invalid: > 500
        }
        form = ClassRoomForm(data=form_data)
        self.assertFalse(form.is_valid())


class TeacherFormValidationTest(TestCase):
    def test_valid_teacher(self):
        """Test that valid data passes"""
        form_data = {
            'teacher_name': 'Dr. John Smith',
        }
        form = TeacherForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_empty_name(self):
        """Test that empty name is rejected"""
        form_data = {
            'teacher_name': '  ',  # Invalid
        }
        form = TeacherForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_short_name(self):
        """Test that single character name is rejected"""
        form_data = {
            'teacher_name': 'A',  # Invalid: < 2 chars
        }
        form = TeacherForm(data=form_data)
        self.assertFalse(form.is_valid())


print("Validation tests created successfully!")
print("Run tests with: python manage.py test timetable.test_validation")
