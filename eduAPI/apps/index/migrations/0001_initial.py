# Generated by Django 2.0.6 on 2020-11-05 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_show', models.BooleanField(default=False, verbose_name='展示与否')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('create_time', models.DateField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateField(auto_now=True, verbose_name='修改时间')),
                ('ordering', models.IntegerField(default=1, verbose_name='序号')),
                ('img', models.ImageField(max_length=255, upload_to='banner', verbose_name='轮播图')),
                ('title', models.CharField(max_length=100, verbose_name='标题')),
                ('link', models.CharField(max_length=255, verbose_name='链接')),
            ],
            options={
                'verbose_name': '轮播图表',
                'verbose_name_plural': '轮播图表',
                'db_table': 't_banner',
            },
        ),
        migrations.CreateModel(
            name='Nav',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_show', models.BooleanField(default=False, verbose_name='展示与否')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否删除')),
                ('create_time', models.DateField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateField(auto_now=True, verbose_name='修改时间')),
                ('ordering', models.IntegerField(default=1, verbose_name='序号')),
                ('title', models.CharField(max_length=50, verbose_name='导航标题')),
                ('link', models.CharField(max_length=255, verbose_name='链接')),
                ('position', models.IntegerField(choices=[(1, 'header'), (2, 'footer')], default=1, verbose_name='位置')),
                ('is_site', models.BooleanField(default=False, verbose_name='是否为外部链接')),
            ],
            options={
                'verbose_name': '导航栏表',
                'verbose_name_plural': '导航栏表',
                'db_table': 't_nav',
            },
        ),
    ]
