# Generated by Django 5.1.6 on 2025-03-12 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_course_image_student_profile_picture_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='profile_picture',
            field=models.ImageField(blank=True, default='images/profiles/profile.jpg', null=True, upload_to='images/student_profiles/'),
        ),
    ]
