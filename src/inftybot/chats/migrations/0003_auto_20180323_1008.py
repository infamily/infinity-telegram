# Generated by Django 2.0.2 on 2018-03-23 10:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('chats', '0002_auto_20180320_1241'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='chat',
            name='categories',
            field=models.ManyToManyField(to='chats.ChatCategory'),
        ),
    ]