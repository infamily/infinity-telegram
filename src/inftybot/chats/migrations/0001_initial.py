# Generated by Django 2.0.2 on 2018-03-02 13:47

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('channel', 'Channel'), ('group', 'Group'), ('private', 'Private')],
                                          max_length=24, verbose_name='Chat type')),
            ],
        ),
        migrations.CreateModel(
            name='ChatData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data',
                 django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, verbose_name='Session data')),
                ('chat', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='chats.Chat',
                                              verbose_name='Chat reference')),
            ],
        ),
    ]