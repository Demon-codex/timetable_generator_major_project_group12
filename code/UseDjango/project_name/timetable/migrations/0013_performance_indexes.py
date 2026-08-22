# Generated manually for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0012_departmenttimetablemodel_fitness'),
    ]

    operations = [
        # Add composite index for year-department queries
        migrations.AddIndex(
            model_name='yearsetupmodel',
            index=models.Index(fields=['department', 'year_name'], name='year_dept_idx'),
        ),
        
        # Add index for fitness score to optimize sorting
        migrations.AddIndex(
            model_name='departmenttimetablemodel',
            index=models.Index(fields=['-fitness', '-created_at'], name='tt_fitness_idx'),
        ),
        
        # Add index for created_at to optimize timetable list sorting
        migrations.AddIndex(
            model_name='departmenttimetablemodel',
            index=models.Index(fields=['-created_at'], name='tt_created_idx'),
        ),
    ]
