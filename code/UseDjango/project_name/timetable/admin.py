from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    setupModel, teacherModel, classRoomModel, labRoomModel,
    recessModel, yearSetupModel, yearClassRoomModel, yearLabRoomModel,
    DepartmentTimetableModel,
)


@admin.register(setupModel)
class SetupModelAdmin(ModelAdmin):
    list_display   = ('department_name', 'start_time', 'end_time', 'number_of_days')
    search_fields  = ('department_name',)
    list_per_page  = 25


@admin.register(teacherModel)
class TeacherModelAdmin(ModelAdmin):
    list_display   = ('teacher_name', 'department')
    search_fields  = ('teacher_name',)
    list_filter    = ('department',)
    list_per_page  = 25


@admin.register(classRoomModel)
class ClassRoomModelAdmin(ModelAdmin):
    list_display   = ('classroom_id', 'department', 'classroom_capacity')
    search_fields  = ('classroom_id',)
    list_filter    = ('department',)
    list_per_page  = 25


@admin.register(labRoomModel)
class LabRoomModelAdmin(ModelAdmin):
    list_display   = ('labroom_id', 'department', 'labroom_capacity')
    search_fields  = ('labroom_id',)
    list_filter    = ('department',)
    list_per_page  = 25


@admin.register(recessModel)
class RecessModelAdmin(ModelAdmin):
    list_display   = ('department', 'recess_start_time', 'recess_end_time')
    list_filter    = ('department',)
    list_per_page  = 25


@admin.register(yearSetupModel)
class YearSetupModelAdmin(ModelAdmin):
    list_display   = ('year_name', 'department', 'total_students', 'number_of_students_in_batch')
    search_fields  = ('year_name',)
    list_filter    = ('department',)
    list_per_page  = 25


@admin.register(yearClassRoomModel)
class YearClassRoomModelAdmin(ModelAdmin):
    list_display   = ('__str__', 'year')
    list_filter    = ('year__department',)
    list_per_page  = 25


@admin.register(yearLabRoomModel)
class YearLabRoomModelAdmin(ModelAdmin):
    list_display   = ('__str__', 'year')
    list_filter    = ('year__department',)
    list_per_page  = 25


@admin.register(DepartmentTimetableModel)
class DepartmentTimetableModelAdmin(ModelAdmin):
    list_display   = ('name', 'department', 'fitness', 'created_at')
    list_filter    = ('department',)
    search_fields  = ('name',)
    readonly_fields = ('created_at', 'fitness')
    list_per_page  = 25