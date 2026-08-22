from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

# first we import the model 
from .models import setupModel, recessModel, teacherModel, classRoomModel, labRoomModel


# importing years models
from .models import yearSetupModel
# inline formsts, for models who are related to setupModel via foreign key

from django.forms import inlineformset_factory
class setup_form(forms.ModelForm):
    # django would automatically create form fields based on the model fields
    class Meta:
        model = setupModel
        fields = [
                 'department_name',
                 'start_time', 
                 'end_time',
                 'number_of_days',
                 'hours_in_lecture',
                 'hours_in_practical',

                ]
        exclude = ['hours_in_lecture', 'hours_in_practical'] # excluding these fields so that it wont be displayed in form
        widgets = {
            'department_name': forms.TextInput(attrs={'class': 'input'}),
            'start_time': forms.TimeInput(attrs={'class': 'input', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'input', 'type': 'time'}),
            'number_of_days': forms.NumberInput(attrs={'class': 'input'}),
            'hours_in_lecture': forms.NumberInput(attrs={'class': 'input'}),
            'hours_in_practical': forms.NumberInput(attrs={'class': 'input'}),
        }
    
    def clean_department_name(self):
        department_name = self.cleaned_data.get('department_name')
        if not department_name or not department_name.strip():
            raise ValidationError("Department name cannot be empty.")
        if len(department_name.strip()) < 2:
            raise ValidationError("Department name must be at least 2 characters long.")
        
        # Check for duplicate department name (case-insensitive)
        department_name_stripped = department_name.strip()
        existing_dept = setupModel.objects.filter(
            department_name__iexact=department_name_stripped
        )
        
        # Exclude current instance if editing
        if self.instance and self.instance.pk:
            existing_dept = existing_dept.exclude(pk=self.instance.pk)
        
        if existing_dept.exists():
            raise ValidationError(f'Department "{department_name_stripped}" already exists. Please choose a different name.')
        
        return department_name_stripped
    
    def clean_number_of_days(self):
        number_of_days = self.cleaned_data.get('number_of_days')
        if number_of_days is None:
            raise ValidationError("Number of days is required.")
        if number_of_days < 1 or number_of_days > 7:
            raise ValidationError("Number of days must be between 1 and 7.")
        return number_of_days
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("End time must be after start time.")
        
        return cleaned_data


class RecessForm(forms.ModelForm):
    class Meta:
        model = recessModel
        fields = ['recess_start_time', 'recess_end_time']
        labels = {
            'recess_start_time': 'Recess Start Time',
            'recess_end_time': 'Recess End Time',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        recess_start = cleaned_data.get('recess_start_time')
        recess_end = cleaned_data.get('recess_end_time')
        
        if recess_start and recess_end:
            if recess_end <= recess_start:
                raise ValidationError("Recess end time must be after recess start time.")
        
        return cleaned_data


class TeacherForm(forms.ModelForm):
    class Meta:
        model = teacherModel
        fields = ['teacher_name']
        labels = {
            'teacher_name': 'Teacher Name',
        }
    
    def clean_teacher_name(self):
        teacher_name = self.cleaned_data.get('teacher_name')
        if not teacher_name or not teacher_name.strip():
            raise ValidationError("Teacher name cannot be empty.")
        if len(teacher_name.strip()) < 2:
            raise ValidationError("Teacher name must be at least 2 characters long.")
        
        # Check for duplicate teacher name within the same department (if instance has department)
        teacher_name_stripped = teacher_name.strip()
        if hasattr(self.instance, 'department') and self.instance.department:
            existing_teacher = teacherModel.objects.filter(
                department=self.instance.department,
                teacher_name__iexact=teacher_name_stripped
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing_teacher = existing_teacher.exclude(pk=self.instance.pk)
            
            if existing_teacher.exists():
                raise ValidationError(f'Teacher "{teacher_name_stripped}" already exists in this department.')
        
        return teacher_name_stripped


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = classRoomModel
        fields = ['classroom_id', 'classroom_capacity']
        labels = {
            'classroom_id': 'Classroom ID',
            'classroom_capacity': 'Capacity',
        }
    
    def clean_classroom_id(self):
        classroom_id = self.cleaned_data.get('classroom_id')
        if not classroom_id or not classroom_id.strip():
            raise ValidationError("Classroom ID cannot be empty.")
        
        # Check for duplicate classroom ID within the same department
        classroom_id_stripped = classroom_id.strip()
        if hasattr(self.instance, 'department') and self.instance.department:
            existing_classroom = classRoomModel.objects.filter(
                department=self.instance.department,
                classroom_id__iexact=classroom_id_stripped
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing_classroom = existing_classroom.exclude(pk=self.instance.pk)
            
            if existing_classroom.exists():
                raise ValidationError(f'Classroom "{classroom_id_stripped}" already exists in this department.')
        
        return classroom_id_stripped
    
    def clean_classroom_capacity(self):
        capacity = self.cleaned_data.get('classroom_capacity')
        if capacity is None:
            raise ValidationError("Classroom capacity is required.")
        if capacity <= 0:
            raise ValidationError("Classroom capacity must be greater than 0.")
        if capacity > 500:
            raise ValidationError("Classroom capacity seems unrealistic (max 500).")
        return capacity


class LabRoomForm(forms.ModelForm):
    class Meta:
        model = labRoomModel
        fields = ['labroom_id', 'labroom_capacity']
        labels = {
            'labroom_id': 'Lab Room ID',
            'labroom_capacity': 'Capacity',
        }
    
    def clean_labroom_id(self):
        labroom_id = self.cleaned_data.get('labroom_id')
        if not labroom_id or not labroom_id.strip():
            raise ValidationError("Lab room ID cannot be empty.")
        
        # Check for duplicate lab room ID within the same department
        labroom_id_stripped = labroom_id.strip()
        if hasattr(self.instance, 'department') and self.instance.department:
            existing_labroom = labRoomModel.objects.filter(
                department=self.instance.department,
                labroom_id__iexact=labroom_id_stripped
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing_labroom = existing_labroom.exclude(pk=self.instance.pk)
            
            if existing_labroom.exists():
                raise ValidationError(f'Lab room "{labroom_id_stripped}" already exists in this department.')
        
        return labroom_id_stripped
    
    def clean_labroom_capacity(self):
        capacity = self.cleaned_data.get('labroom_capacity')
        if capacity is None:
            raise ValidationError("Lab room capacity is required.")
        if capacity <= 0:
            raise ValidationError("Lab room capacity must be greater than 0.")
        if capacity > 500:
            raise ValidationError("Lab room capacity seems unrealistic (max 500).")
        return capacity


# =============================================
# Custom formsets for duplicate checking within submitted data
class BaseTeacherFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        
        teacher_names = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                teacher_name = form.cleaned_data.get('teacher_name')
                if teacher_name:
                    teacher_name_lower = teacher_name.lower()
                    if teacher_name_lower in teacher_names:
                        raise ValidationError(f'Duplicate teacher name: "{teacher_name}". Each teacher must have a unique name.')
                    teacher_names.append(teacher_name_lower)

class BaseClassRoomFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        
        classroom_ids = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                classroom_id = form.cleaned_data.get('classroom_id')
                if classroom_id:
                    classroom_id_lower = classroom_id.lower()
                    if classroom_id_lower in classroom_ids:
                        raise ValidationError(f'Duplicate classroom ID: "{classroom_id}". Each classroom must have a unique ID.')
                    classroom_ids.append(classroom_id_lower)

class BaseLabRoomFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        
        labroom_ids = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                labroom_id = form.cleaned_data.get('labroom_id')
                if labroom_id:
                    labroom_id_lower = labroom_id.lower()
                    if labroom_id_lower in labroom_ids:
                        raise ValidationError(f'Duplicate lab room ID: "{labroom_id}". Each lab room must have a unique ID.')
                    labroom_ids.append(labroom_id_lower)

# =============================================
RecessFormSet = inlineformset_factory(
    setupModel,        # parent model
    recessModel,      # related model
    form=RecessForm,  # form with validation
    fields=['recess_start_time', 'recess_end_time'],  # fields to include in the formset
    extra=1,           # how many blank forms to display
    can_delete=True    # allow deleting existing recesses
)
TeacherFormSet = inlineformset_factory(
    setupModel,        # parent model
    teacherModel,      # related model
    form=TeacherForm, # for custom labels
    formset=BaseTeacherFormSet,  # custom formset for duplicate checking
    fields=['teacher_name'],  # fields to include in the formset
    
    extra=1,           # how many blank forms to display
    can_delete=True    # allow deleting existing teachers

)

ClassRoomFormSet = inlineformset_factory(
    setupModel,        # parent model
    classRoomModel,      # related model
    form=ClassRoomForm, # for custom labels
    formset=BaseClassRoomFormSet,  # custom formset for duplicate checking
    fields=['classroom_id', 'classroom_capacity'],  # fields to include in the formset
    extra=1,           # how many blank forms to display
    can_delete=True    # allow deleting existing teachers
)

LabFormSet = inlineformset_factory(
    setupModel,        # parent model
    labRoomModel,      # related model
    form=LabRoomForm, # for custom labels
    formset=BaseLabRoomFormSet,  # custom formset for duplicate checking
    fields=['labroom_id','labroom_capacity'],  # fields to include in the formset
    extra=1,           # how many blank forms to display
    can_delete=True    # allow deleting existing teachers
)
# =========================================== forms needed for years ============================================

# the main one, to which other models will be related
class yearSetupForm(forms.ModelForm):
    class Meta:
        model = yearSetupModel
        fields = [
            'year_name',
            'total_students',
            'number_of_students_in_batch'
        ]
    
    def clean_year_name(self):
        year_name = self.cleaned_data.get('year_name')
        if not year_name or not year_name.strip():
            raise ValidationError("Year name cannot be empty.")
        
        # Check for duplicate year name within the same department
        year_name_stripped = year_name.strip()
        if hasattr(self.instance, 'department') and self.instance.department:
            existing_year = yearSetupModel.objects.filter(
                department=self.instance.department,
                year_name__iexact=year_name_stripped
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing_year = existing_year.exclude(pk=self.instance.pk)
            
            if existing_year.exists():
                raise ValidationError(f'Year "{year_name_stripped}" already exists in this department.')
        
        return year_name_stripped
    
    def clean_total_students(self):
        total_students = self.cleaned_data.get('total_students')
        if total_students is None:
            raise ValidationError("Total students is required.")
        if total_students <= 0:
            raise ValidationError("Total students must be greater than 0.")
        if total_students > 1000:
            raise ValidationError("Total students seems unrealistic (max 1000).")
        return total_students
    
    def clean_number_of_students_in_batch(self):
        batch_size = self.cleaned_data.get('number_of_students_in_batch')
        if batch_size is None:
            raise ValidationError("Batch size is required.")
        if batch_size <= 0:
            raise ValidationError("Batch size must be greater than 0.")
        return batch_size
    
    def clean(self):
        cleaned_data = super().clean()
        total_students = cleaned_data.get('total_students')
        batch_size = cleaned_data.get('number_of_students_in_batch')
        
        if total_students and batch_size:
            if batch_size > total_students:
                raise ValidationError("Batch size cannot be greater than total students.")
        
        return cleaned_data




from .models import subjectModel, teacherModel

class SubjectForm(forms.ModelForm):
    class Meta:
        model = subjectModel
        fields = ['subject_name', 'teachers', 'hours_per_week']
        widgets = {
            'teachers': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        self.year_instance = kwargs.pop('year', None)  # Store year for duplicate checking
        super().__init__(*args, **kwargs)

        if department:
            self.fields['teachers'].queryset = teacherModel.objects.filter(
                department=department
            )
    
    def clean_subject_name(self):
        subject_name = self.cleaned_data.get('subject_name')
        if not subject_name or not subject_name.strip():
            raise ValidationError("Subject name cannot be empty.")
        
        # Check for duplicate subject name within the same year
        subject_name_stripped = subject_name.strip()
        year = self.year_instance or (self.instance.year if self.instance and self.instance.pk else None)
        
        if year:
            existing_subject = subjectModel.objects.filter(
                year=year,
                subject_name__iexact=subject_name_stripped
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing_subject = existing_subject.exclude(pk=self.instance.pk)
            
            if existing_subject.exists():
                raise ValidationError(f'Subject "{subject_name_stripped}" already exists for this year.')
        
        return subject_name_stripped
    
    def clean_hours_per_week(self):
        hours = self.cleaned_data.get('hours_per_week')
        if hours is None:
            raise ValidationError("Hours per week is required.")
        if hours <= 0:
            raise ValidationError("Hours per week must be greater than 0.")
        if hours > 40:
            raise ValidationError("Hours per week seems unrealistic (max 40).")
        return hours
    
    def clean_teachers(self):
        teachers = self.cleaned_data.get('teachers')
        if not teachers or teachers.count() == 0:
            raise ValidationError("At least one teacher must be selected.")
        return teachers


from .models import practicalModel
class PracticalForm(forms.ModelForm):
    class Meta:
        model = practicalModel
        fields = ['practical_name', 'teachers', 'hours_per_week']
        widgets = {
            'teachers': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        self.year_instance = kwargs.pop('year', None)  # Store year for duplicate checking
        super().__init__(*args, **kwargs)

        if department:
            self.fields['teachers'].queryset = teacherModel.objects.filter(
                department=department
            )
    
    def clean_practical_name(self):
        practical_name = self.cleaned_data.get('practical_name')
        if not practical_name or not practical_name.strip():
            raise ValidationError("Practical name cannot be empty.")
        
        # Check for duplicate practical name within the same year
        practical_name_stripped = practical_name.strip()
        year = self.year_instance or (self.instance.year if self.instance and self.instance.pk else None)
        
        if year:
            existing_practical = practicalModel.objects.filter(
                year=year,
                practical_name__iexact=practical_name_stripped
            )
            
            # Exclude current instance if editing
            if self.instance and self.instance.pk:
                existing_practical = existing_practical.exclude(pk=self.instance.pk)
            
            if existing_practical.exists():
                raise ValidationError(f'Practical "{practical_name_stripped}" already exists for this year.')
        
        return practical_name_stripped
    
    def clean_hours_per_week(self):
        hours = self.cleaned_data.get('hours_per_week')
        if hours is None:
            raise ValidationError("Hours per week is required.")
        if hours <= 0:
            raise ValidationError("Hours per week must be greater than 0.")
        if hours > 40:
            raise ValidationError("Hours per week seems unrealistic (max 40).")
        return hours
    
    def clean_teachers(self):
        teachers = self.cleaned_data.get('teachers')
        if not teachers or teachers.count() == 0:
            raise ValidationError("At least one teacher must be selected.")
        return teachers


from .models import yearLabRoomModel

class YearLabRoomForm(forms.ModelForm):
    class Meta:
        model = yearLabRoomModel
        fields = ['labrooms']
        widgets = {
            'labrooms': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)

        if department:
            self.fields['labrooms'].queryset = (
                labRoomModel.objects.filter(department=department)
            )





from .models import yearClassRoomModel

class YearClassRoomForm(forms.ModelForm):
    class Meta:
        model = yearClassRoomModel
        fields = ['classrooms']
        widgets = {
            'classrooms': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)

        if department:
            self.fields['classrooms'].queryset = (
                classRoomModel.objects.filter(department=department)
            )

# form for editing number of students in each batch for a year
class EditYearStudentsInBatchForm(forms.ModelForm):
    class Meta:
        model = yearSetupModel
        fields = ['number_of_students_in_batch']


# form for editing total number of students in a year
class EditYearTotalStudentsForm(forms.ModelForm):
    class Meta:
        model = yearSetupModel
        fields = ['total_students']
