from django.urls import path
from django.views.generic import RedirectView
from . import views


app_name = 'timetable'
# i created this urlpatterns of app timetable
urlpatterns = [
    path('', RedirectView.as_view(url='home/', permanent=False)),
    path('home/', views.home, name='home'),
    path('setup/', views.setup, name='setup'),
    path('setupform/', views.setupForm, name='setupFormUrlIdentifier'),
    path('setupform/<int:pk>/edit/', views.setupForm, name='setup_edit'),
    # delete deparmment whole data button
    path('setupdelete/<int:pk>/', views.setup_delete, name='setup_delete'),

    # for viewing that particular department years
    path('years/<int:pk>/', views.years, name='years'),


    # for adding years to that department
    path('department/<int:department_id>/year/add/', views.yearsSetupForm, name='yearsSetupForm'),

    # for adding lectures in a year
    path(
        'department/<int:department_id>/year/<int:year_id>/subject/add/',
        views.add_subject,
        name='add_subject'
    ),
    # for deleting a year
    path(
        'department/<int:department_id>/year/<int:year_id>/delete/',
        views.delete_year,
        name='delete_year'
    ),
    # for deleting a subject
    path(
        'department/<int:department_id>/subject/<int:subject_id>/delete/',
        views.delete_subject,
        name='delete_subject'
    ),
    # for editing a subject
    path(
        'department/<int:department_id>/subject/<int:subject_id>/edit/',
        views.edit_subject,
        name='edit_subject'
    ),

    path(
        'department/<int:department_id>/year/<int:year_id>/practical/add/',
        views.add_practical,
        name='add_practical'
    ),

    path(
        'department/<int:department_id>/practical/<int:practical_id>/delete/',
        views.delete_practical,
        name='delete_practical'
    ),
    # for editing a practical
    path(
        'department/<int:department_id>/practical/<int:practical_id>/edit/',
        views.edit_practical,
        name='edit_practical'
    ),
    # path for editing a year number of student in each batch
    path('department/<int:department_id>/year/<int:year_id>/edit/', views.edit_year_students_in_batch, name ='edit_year_students_in_batch'),

    # path for editing a year total number of students
    path('department/<int:department_id>/year/<int:year_id>/edit/total/', views.edit_year_total_students, name ='edit_year_total_students'),
    
    # path for adding class rooms for a year in a department
    path(
        'department/<int:department_id>/year/<int:year_id>/classroom/add/',
        views.add_year_classrooms,
        name='add_year_classrooms'
    ),
    path(
        'department/<int:department_id>/year/<int:year_id>/labroom/add/',
        views.add_year_labrooms,
        name='add_year_labrooms'
    ),
    # ===============================================================================================
    # for generating the data needed for generating the New timetables of that department
    path('department/<int:department_id>/timetable/generate/', views.generate_timetableData, name='generate_timetable'), 


    # for viewing the list of saved timetables of that department
    path(
        'department/<int:department_id>/savedtimetables/',
        views.department_saved_timetable_list,
        name='department_saved_timetable_list'
    ),

    # for viewing a particular saved timetable
    path(
        "timetable/<int:tt_id>/savedtimetables/view/",
        views.view_saved_timetable,
        name="view_saved_timetable"
    ),

    # for deleting a particular saved timetable
    path(
        "timetable/<int:tt_id>/delete/",
        views.delete_saved_timetable,
        name="delete_saved_timetable"
    ),

    # for comparing timetables
    path(
        "department/<int:department_id>/compare/",
        views.compare_timetables,
        name="compare_timetables"
    ),

    # for exporting timetable to Excel
    path(
        "timetable/<int:tt_id>/export/excel/",
        views.export_timetable_excel,
        name="export_timetable_excel"
    ),

    # for exporting timetable to PDF
    path(
        "timetable/<int:tt_id>/export/pdf/",
        views.export_timetable_pdf,
        name="export_timetable_pdf"
    ),

    # Batch operations
    path(
        "department/<int:department_id>/batch/delete/subjects/",
        views.batch_delete_subjects,
        name="batch_delete_subjects"
    ),
    path(
        "department/<int:department_id>/batch/delete/practicals/",
        views.batch_delete_practicals,
        name="batch_delete_practicals"
    ),
    path(
        "department/<int:department_id>/batch/delete/years/",
        views.batch_delete_years,
        name="batch_delete_years"
    ),
    path(
        "batch/delete/timetables/",
        views.batch_delete_timetables,
        name="batch_delete_timetables"
    ),

    #===============================================================================================

    
]