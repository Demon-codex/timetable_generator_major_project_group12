from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator

class setupModel(models.Model):
    department_name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    # this needs validation to ensure positive int and less than equal to 7
    number_of_days = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(7)
        ]
    )

    # i am going to set default becasuse i cant handle other values in timetable generation, therefore user cant change and is not displayed in form by using exclude in form
    hours_in_lecture = models.IntegerField(default=1)
    hours_in_practical = models.IntegerField(default=2)



    def __str__(self):
        return self.department_name

class recessModel(models.Model):
    # since one department has many recesses we use foreign key
    department = models.ForeignKey(
        setupModel,
        on_delete=models.CASCADE,
        related_name='relatedNameRecesses' # to access recesses of a depatment
    )
    recess_start_time = models.TimeField()
    recess_end_time = models.TimeField()

    def __str__(self):
        return f"Recess for {self.department.department_name} from {self.recess_start_time} to {self.recess_end_time}"



class teacherModel(models.Model):
    # since one department has many teachers we use foreign key

    department = models.ForeignKey(
        setupModel,
        on_delete=models.CASCADE,
        related_name='relatedNameTeachers' # to access teachers of a depatment
    )
    # serial_number = models.IntegerField() its difficult to maintain serial number if we delete any teacher in between
    teacher_name = models.CharField(max_length=100)

    def __str__(self):
        return self.teacher_name
    

class classRoomModel(models.Model):
    # since one department has many classrooms we use foreign key

    department = models.ForeignKey(
        setupModel,
        on_delete=models.CASCADE,
        related_name='relatedNameClassRooms' # to access classRooms of a depatment
    )
    # serial_number = models.IntegerField() its difficult to maintain serial number if we delete any teacher in between
    classroom_id = models.CharField(max_length=100)
    classroom_capacity = models.PositiveIntegerField()


    def __str__(self):
        return self.classroom_id
    
class labRoomModel(models.Model):
    # since one department has many labs we use foreign key

    department = models.ForeignKey(
        setupModel,
        on_delete=models.CASCADE,
        related_name='relatedNameLabRooms' # to access labrooms of a depatment
    )
    # serial_number = models.IntegerField() its difficult to maintain serial number if we delete any teacher in between
    labroom_id = models.CharField(max_length=100)
    labroom_capacity = models.PositiveIntegerField()


    def __str__(self):
        return self.labroom_id
    
# =========================================== models needed for years ============================================

class yearSetupModel(models.Model):
    # since one department has many years we use foreign key

    department = models.ForeignKey(
        setupModel,
        on_delete=models.CASCADE,
        related_name='relatedNameYearSetupModel' # to access teachers of a depatment
    )
    # serial_number = models.IntegerField() its difficult to maintain serial number if we delete any teacher in between
    year_name = models.CharField(max_length=100)
    total_students = models.PositiveIntegerField()

    # i dont know what to do with this
    number_of_students_in_batch = models.PositiveIntegerField()
    

    def __str__(self):
        return self.year_name
    

class subjectModel(models.Model):
    year = models.ForeignKey(
        yearSetupModel,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    subject_name = models.CharField(max_length=100)

    teachers = models.ManyToManyField(teacherModel)
    hours_per_week = models.PositiveIntegerField()

    def __str__(self):
        return self.subject_name

class practicalModel(models.Model):
    year = models.ForeignKey(
        yearSetupModel,
        on_delete=models.CASCADE,
        related_name='practicals'
    )
    practical_name = models.CharField(max_length=100)
    teachers = models.ManyToManyField(teacherModel)
    hours_per_week = models.PositiveIntegerField()
    def __str__(self):
        return self.practical_name

# for storing allocated labrooms and classrooms for a year in a department
class yearLabRoomModel(models.Model):
    year = models.OneToOneField(
        yearSetupModel,
        on_delete=models.CASCADE,
        related_name='yearLabRoomsAllocated'
    )
    labrooms = models.ManyToManyField(labRoomModel)

    def __str__(self):
        return self.year.year_name + " Lab Rooms"
    
    
class yearClassRoomModel(models.Model):
    year = models.OneToOneField(
        yearSetupModel,
        on_delete=models.CASCADE,
        related_name='yearClassRoomsAllocated'
    )
    classrooms = models.ManyToManyField(classRoomModel)

    def __str__(self):
        return self.year.year_name + " Class Rooms"   
    
#==========================================
# for storing timetables of all years that was generated, can store multiple timetables for same department
class DepartmentTimetableModel(models.Model):
    department = models.ForeignKey(
        setupModel,
        on_delete=models.CASCADE,
        related_name= 'realatedNameSavedTimetablesOfDepartment'
    )
    name = models.CharField(max_length=100)  # name of the timetables group given by user
    # 
    displayTimetable = models.JSONField()  # json of timetables formatted for display
    # json of all years timetables combined

    fitness = models.FloatField(null=True, blank=True) # fitness score of the timetables

    # chart data
    teacherYearChart = models.JSONField(default=dict)  # default to empty dict
    lectureHoursTable = models.JSONField(default=dict)  # default to empty dict
    practicalHoursTable = models.JSONField(default=dict)  # default to empty dict

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.department} - {self.name}"