# Generated by Django 5.2 on 2025-07-06 01:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_aboutpagecontent_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='姓名')),
                ('title', models.CharField(max_length=100, verbose_name='职位')),
                ('email', models.EmailField(max_length=254, verbose_name='邮箱')),
                ('phone', models.CharField(max_length=50, verbose_name='电话')),
                ('location', models.CharField(max_length=100, verbose_name='地址')),
                ('linkedin', models.URLField(blank=True, verbose_name='LinkedIn')),
                ('github', models.URLField(blank=True, verbose_name='GitHub')),
                ('twitter', models.URLField(blank=True, verbose_name='Twitter')),
                ('website', models.URLField(blank=True, verbose_name='个人网站')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AboutSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='专业总结')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='EducationExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree', models.CharField(max_length=100, verbose_name='学位')),
                ('institution', models.CharField(max_length=100, verbose_name='学校')),
                ('location', models.CharField(blank=True, max_length=100, verbose_name='地点')),
                ('period', models.CharField(blank=True, max_length=100, verbose_name='时间段')),
                ('order', models.PositiveIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SkillGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100, verbose_name='技能类别')),
                ('order', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='WorkExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=100, verbose_name='职位')),
                ('company', models.CharField(max_length=100, verbose_name='公司')),
                ('location', models.CharField(blank=True, max_length=100, verbose_name='地点')),
                ('period', models.CharField(max_length=100, verbose_name='时间段')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='排序')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='EducationCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='课程名称')),
                ('order', models.PositiveIntegerField(default=0)),
                ('education', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='blog.educationexperience')),
            ],
        ),
        migrations.CreateModel(
            name='EducationProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='项目名称')),
                ('description', models.TextField(blank=True, verbose_name='项目描述')),
                ('order', models.PositiveIntegerField(default=0)),
                ('education', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='blog.educationexperience')),
            ],
        ),
        migrations.CreateModel(
            name='SkillItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='技能名称')),
                ('order', models.PositiveIntegerField(default=0)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='blog.skillgroup')),
            ],
        ),
        migrations.CreateModel(
            name='WorkResponsibility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=300, verbose_name='职责描述')),
                ('order', models.PositiveIntegerField(default=0)),
                ('experience', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responsibilities', to='blog.workexperience')),
            ],
        ),
    ]
